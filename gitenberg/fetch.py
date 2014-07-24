#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches a folder of book files from a remote to local
"""

from __future__ import print_function
import os

import sh

from .path import path_to_library_book
from .path import path_to_pg_book


class Book():

    def __init__(self, book_id):
        """
        A Book:
          - has a shelf (folder in library directory)
          - has an `author`
          - has a `title`
        """
        self.book_id = book_id
        self.book_path = path_to_library_book(book_id)

        self.make_shelf_in_library()
        self.rsync_files_from_remote()

    def make_shelf_in_library(self):
        try:
            os.makedirs(self.book_path)
        except OSError:
            # FIXME logging.debug
            print("Folder {0} already exists".format(self.book_path))

    def rsync_files_from_remote(self):
        # FIXME: check for presence of folder as expected before fetch
        sh.rsync(
            '-rvhz',
            'ftp@ftp.ibiblio.org::gutenberg/{0}'.format(path_to_pg_book(self.book_id)),
            self.book_path
        )
        if len(sh.ls(self.book_path)) == 0:
            raise


def fetch(book_id):
    # TODO: if make is passed, pass the ebook to make
    Book(book_id)
