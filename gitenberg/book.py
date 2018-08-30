#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import gc
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

logger = logging.getLogger(__name__)

class Book():
    """ An index card tells you where a book lives
        `book_id` is PG's unique book id
        `remote_path` is where it should live on PG servers
        `srepo_name` is the name the repo should have on GitHub
        `local_path` is where it IS stored locally
    """

    def __init__(self, book_id, repo_name=None, library_path='./library'):
        # rename to avoid confusion
        arg_repo_name = repo_name
        self.local_path = None

        # do config
        self.library_path = config.get_library_path(library_path)

        # parse the inputs to figure out the book
        if arg_repo_name and not book_id:
            book_id = arg_repo_name.split('_')[-1]

        if book_id:
            self.book_id = str(book_id)
            self.repo_name = get_repo_name(self.book_id)
            self.set_existing_local_path(self.book_id)
        else:
            self.book_id = None
            self.repo_name = None

        # check if there's a directory named with the arg_repo_name
        if arg_repo_name and not self.local_path:
            self.set_existing_local_path(arg_repo_name)

        # or, check if there's a directory named with the github name
        if self.repo_name and not self.local_path:
            self.set_existing_local_path(self.repo_name)

        # set up the local repo
        if self.local_path:
            self.local_repo = LocalRepo(self.local_path)
        else:
            self.local_repo = None

        # set up the Github connection
        self.github_repo = GithubRepo(self)

    def set_existing_local_path(self, name):
        path = os.path.join(self.library_path, name)
        if os.path.exists(path):
            self.local_path = path
        
    def make_local_path(self):
        path = os.path.join(self.library_path, self.book_id)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                self.local_path = path
            except OSError:
                logger.error("couldn't make path: {}".format(path))
            finally:  # weird try-except-finally, I know
                os.chmod(path, 0o777)

    def parse_book_metadata(self, rdf_library=None):
        # cloned repo
        if self.local_repo and self.local_repo.metadata_file:
            self.meta = Pandata(datafile=self.local_repo.metadata_file)
            return 'update metadata '

        # named repo
        if self.repo_name:
            named_path = os.path.join(self.library_path, self.repo_name, 'metadata.yaml')
            if os.path.exists(named_path):
                self.meta = Pandata(datafile=named_path)
                return 'update metadata '

        # new repo
        if not rdf_library:
            self.meta = BookMetadata(self, rdf_library=config.data.get("rdf_library",""))
        else:
            self.meta = BookMetadata(self, rdf_library=rdf_library)

        # preserve existing repo names
        if self.repo_name:
            self.meta.metadata['_repo'] = self.repo_name
        else:
            self.format_title()
        return 'new repo '

    @property
    def remote_path(self):
        """ turns an ebook_id into a path on PG's server(s)
            4443  -> 4/4/4/4443/ """
        # TODO: move this property into independent object for PG
        path_parts = list(self.book_id[:-1])
        path_parts.append(self.book_id)
        return os.path.join(*path_parts) + '/'

    def fetch(self):
        """ just pull files from PG
        """
        self.make_local_path()
        fetcher = BookFetcher(self)
        fetcher.fetch()

    def clone_from_github(self):
        if self.local_repo:
            # don't need to clone the repo
            # perhaps we should delete the repo and refresh?
            pass
        else:
            self.local_repo = clone(self.repo_name)
            self.local_path = self.local_repo.repo_path
            self.parse_book_metadata() # reload with cloned metadata.yaml

    def make(self):
        """ turn fetched files into a local repo, make auxiliary files
        """
        logger.debug("preparing to add all git files")
        num_added = self.local_repo.add_all_files()
        if num_added:
            self.local_repo.commit("Initial import from Project Gutenberg")

        file_handler = NewFilesHandler(self)
        file_handler.add_new_files()

        num_added = self.local_repo.add_all_files()
        if num_added:
            self.local_repo.commit(
                "Updates Readme, contributing, license files, cover, metadata."
            )

    def save_meta(self):
        self.meta.dump_file(os.path.join(self.local_path, 'metadata.yaml'))

    def push(self):
        """ create a github repo and push the local repo into it
        """
        self.github_repo.create_and_push()
        return self.github_repo.repo

    def update(self, message='Update files'):
        """ commit changes
        """
        self.github_repo.update(message)

    def tag(self, version='bump', message=''):
        """ tag and commit
        """
        self.clone_from_github()
        self.github_repo.tag(version, message=message)

    def repo(self):
        if self.repo_name:
            return self.github_repo.github.repository(GITHUB_ORG, self.repo_name)

    def all(self):
        try:
            self.fetch()
            if not self.local_repo:
                self.local_repo = LocalRepo(self.local_path)
            self.make()
            self.push()
            logger.info(u"{0} {1} added".format(self.book_id, self.meta._repo))
        except sh.ErrorReturnCode_12:
            logger.error(u"{0} {1} timeout".format(self.book_id, self.meta._repo))
        except sh.ErrorReturnCode_23:
            logger.error(u"{0} {1} notfound".format(self.book_id, self.meta._repo))
        except github3.GitHubError as e:
            logger.error(u"{0} {1} already".format(self.book_id, self.meta._repo))
        except sh.ErrorReturnCode_1:
            logger.error(u"{0} {1} nopush".format(self.book_id, self.meta._repo))
        finally:
            self.remove()

    def remove(self):
        # otherwise GitPython uses up to many system resources
        gc.collect()
        if self.local_repo:
            self.local_repo.git.git.clear_cache()
        
        shutil.rmtree(self.local_path)

    def format_title(self):
        def asciify(_title):
            _title = unicodedata.normalize('NFD', unicode(_title))
            ascii = True
            out = []
            ok = u"1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM- ',"
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
        logger.debug("%s %s" % (len(repo_title), repo_title))
        self.meta.metadata['_repo'] = repo_title
        return repo_title

    def generate_cover(self):
        if not self.meta:
            self.parse_book_metadata()
        try:
            cover_image = tenprintcover.draw(
                self.meta.title_no_subtitle,
                self.meta.subtitle,
                self.meta.authors_short()
            )
            return cover_image
        except OSError:
            logger.error("OSError, probably Cairo not installed.")
            return None

    def add_covers(self):
        new_covers = []
        comment = ''
        for cover in self.meta.covers:
            #check that the covers are in repo
            cover_path = os.path.join(self.local_path, cover.get("image_path", ""))
            if os.path.isfile(cover_path):
                new_covers.append(cover)
        if len(new_covers) == 0:
            cover_files = self.local_repo.cover_files() if self.local_repo else []
            if cover_files:
                new_covers.append(
                        {"image_path": cover_files[0], "cover_type":"archival"}
                    )
                comment = " added archival cover"
            else:
                with open('{}/cover.png'.format(self.local_path), 'w+') as cover:
                    self.generate_cover().save(cover)
                    new_covers.append(
                            {"image_path": "cover.png", "cover_type":"generated"}
                        )
                comment =  " generated cover"
            if '_version' in self.meta.metadata:
                self.meta.metadata['_version'] =  semver.bump_minor(self.meta._version)
            else:
                self.meta.metadata['_version'] =  '0.1.0'
        self.meta.metadata['covers'] = new_covers
        return comment


