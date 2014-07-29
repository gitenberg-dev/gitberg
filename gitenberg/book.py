#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import shutil

import github3
import sh

from .fetch import BookFetcher
from .make import NewFilesHandler, LocalRepo
from .push import GithubRepo
from .util.catalog import BookMetadata


class Book():
    """ An index card tells you where a book lives
        `book_id` is PG's unique book id
        `remote_path` is where it lives on PG servers
        `local_path` is where it should be stored locally
    """

    def __init__(self, book_id, library_path='./library'):
        self.book_id = str(book_id)
        self.library_path = library_path

    def parse_book_metadata(self, rdf_library=None):
        if not rdf_library:
            self.meta = BookMetadata(self)
        else:
            self.meta = BookMetadata(self, rdf_library=rdf_library)

    @property
    def remote_path(self):
        """ turns an ebook_id into a path on PG's server(s)
            4443  -> 4/4/4/4443/ """
        path_parts = list(self.book_id[:-1])
        path_parts.append(self.book_id)
        return os.path.join(*path_parts) + '/'

    @property
    def local_path(self):
        path_parts = [self.library_path, self.book_id]
        return os.path.join(*path_parts)

    def fetch(self):
        fetcher = BookFetcher(self)
        fetcher.fetch()

    def make(self):
        local_repo = LocalRepo(self)
        local_repo.add_all_files()
        local_repo.commit("Initial import from Project Gutenberg")

        file_handler = NewFilesHandler(self)
        file_handler.add_new_files()

        local_repo.add_all_files()
        local_repo.commit(
            "Adds Readme, contributing and license files to book repo"
        )

    def push(self):
        github_repo = GithubRepo(self)
        github_repo.create_and_push()

    def all(self):
        try:
            self.fetch()
            self.make()
            self.push()
            self.remove()
        except sh.ErrorReturnCode_12:
            logging.error("err00: rsync timed out on {0} {1}: \
                {0} {1}".format(self.book_id, self.meta.title))
        except sh.ErrorReturnCode_23:
            logging.error("err01: can't find remote book on pg server: \
                {0} {1}".format(self.book_id, self.meta.title))
        except github3.GitHubError as e:
            logging.error("err02: This book already exists on github: \
                {0} {1} {2}".format(self.book_id, self.meta.title, e))

    def remove(self):
        shutil.rmtree(self.local_path)
