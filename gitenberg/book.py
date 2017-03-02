#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import shutil

import github3
import semver
import sh
from re import sub
import unicodedata

from . import config
from .clone import clone
from .fetch import BookFetcher
from .make import NewFilesHandler
from .local_repo import LocalRepo
from .parameters import GITHUB_ORG
from .push import GithubRepo
from .util import tenprintcover
from .util.catalog import BookMetadata, get_repo_name
from .metadata.pandata import Pandata


class Book():
    """ An index card tells you where a book lives
        `book_id` is PG's unique book id
        `remote_path` is where it lives on PG servers
        `local_path` is where it should be stored locally
    """

    def __init__(self, book_id, repo_name=None, library_path='./library'):
        if repo_name and not book_id:
            self.repo_name = repo_name
            book_id = repo_name.split('_')[-1]
        else:
            self.repo_name = None
        self.book_id = str(book_id)
        self.local_repo = None
        self.github_repo = GithubRepo(self)
        try:
            self.library_path = config.data.get("library_path",library_path)
        except:
            # no config, used in tests
            self.library_path = library_path

    def parse_book_metadata(self, rdf_library=None):
        if self.local_repo and self.local_repo.metadata_file:
            self.meta = Pandata(datafile=self.local_repo.metadata_file)
            return self.meta._repo
        if not rdf_library:
            self.meta = BookMetadata(self, rdf_library=config.data.get("rdf_library",""))
        else:
            self.meta = BookMetadata(self, rdf_library=rdf_library)
        
        # preserve existing repo names
        if self.repo_name:
            self.meta.metadata['_repo'] = self.repo_name
        else:
            self.format_title()

    @property
    def remote_path(self):
        """ turns an ebook_id into a path on PG's server(s)
            4443  -> 4/4/4/4443/ """
        # TODO: move this property into independent object for PG
        path_parts = list(self.book_id[:-1])
        path_parts.append(self.book_id)
        return os.path.join(*path_parts) + '/'

    @property
    def local_path(self):
        if self.local_repo:
            return self.local_repo.repo_path
        path_parts = [self.library_path, self.book_id]
        return os.path.join(*path_parts)

    def fetch(self):
        """ just pull files from PG
        """
        fetcher = BookFetcher(self)
        fetcher.fetch()
    
    def clone_from_github(self):
        self.local_repo = clone(self.book_id)
        self.repo_name = get_repo_name(self.book_id)
    
    def make(self):
        """ turn fetched files into a local repo, make auxiliary files
        """
        self.local_repo = LocalRepo(self.local_path)
        logging.debug("preparing to add all git files")
        self.local_repo.add_all_files()
        self.local_repo.commit("Initial import from Project Gutenberg")

        file_handler = NewFilesHandler(self)
        file_handler.add_new_files()

        self.local_repo.add_all_files()
        self.local_repo.commit(
            "Adds Readme, contributing and license files to book repo"
        )

    def push(self):
        """ create a github repo and push the local repo into it
        """
        self.github_repo.create_and_push()
        return self.github_repo.repo

    def repo(self):
        if self.repo_name:
            return self.github_repo.github.repository(GITHUB_ORG, repo_name)

    def all(self):
        try:
            self.fetch()
            self.make()
            self.push()
            print u"{0} {1} added".format(self.book_id, self.meta._repo)
        except sh.ErrorReturnCode_12:
            logging.error(u"{0} {1} timeout".format(self.book_id, self.meta._repo))
        except sh.ErrorReturnCode_23:
            logging.error(u"{0} {1} notfound".format(self.book_id, self.meta._repo))
        except github3.GitHubError as e:
            logging.error(u"{0} {1} already".format(self.book_id, self.meta._repo))
        except sh.ErrorReturnCode_1:
            logging.error(u"{0} {1} nopush".format(self.book_id, self.meta._repo))
        finally:

            self.remove()

    def remove(self):
        shutil.rmtree(self.local_path)

    def format_title(self):
        def asciify(_title):
            _title = unicodedata.normalize('NFD', unicode(_title))
            ascii = True
            out = []
            ok=u"1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM- ',"
            for ch in _title:
                if ch in ok:
                    out.append(ch)
                elif unicodedata.category(ch)[0] == ("L"): #a letter
                    out.append(hex(ord(ch)))
                    ascii = False
                elif ch in u'\r\n\t':
                    out.append(u'-')
            return (ascii, sub("[ ',-]+", '-', "".join(out)) )
        
        """ Takes a string and sanitizes it for Github's url name format """
        (ascii, _title) = asciify(self.meta.title)
        if not ascii and self.meta.alternative_title:
            (ascii, _title2) = asciify(self.meta.alternative_title)
            if ascii:
                _title = _title2
        title_length = 99 - len(str(self.book_id)) - 1
        if len(_title) > title_length:
            # if the title was shortened, replace the trailing _ with an ellipsis
            repo_title = "{0}__{1}".format(_title[:title_length], self.book_id)
        else:
            repo_title = "{0}_{1}".format(_title[:title_length], self.book_id)
        # FIXME: log debug, title creation
        #print(len(repo_title), repo_title)
        self.meta.metadata['_repo'] = repo_title
        return repo_title

    def generate_cover(self):
        if not self.meta:
            self.load_book_metadata()
        try:
            cover_image = tenprintcover.draw(
                self.meta.title_no_subtitle, 
                self.meta.subtitle, 
                self.meta.authors_short()
            )
            return cover_image
        except OSError:
            print "OSError, probably Cairo not installed."
            return None

    def add_covers(self):   
        if len(self.meta.covers) == 0:
            cover_files = self.local_repo.cover_files() if self.local_repo else []
            if cover_files:
                self.meta.metadata['covers']=[
                        {"image_path": cover_files[0], "cover_type":"archival"}
                    ]
                return "added archival cover"
            else:         
                with open('{}/cover.png'.format(self.local_path), 'w+') as cover:
                    self.generate_cover().save(cover)
                    self.meta.metadata['covers']=[
                            {"image_path": "cover.png", "cover_type":"generated"}
                        ]
                return "generated cover"
            self.meta.metadata['_version'] =  semver.bump_minor(self.meta._version)
        return None
        
        
