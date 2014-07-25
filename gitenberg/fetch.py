#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches a folder of book files from a remote to local
"""

from __future__ import print_function
import os

import sh


class BookFetcher():

    def __init__(self, book):
        """
        A BookFetcher:
          - makes a shelf (folder in library directory)
          - rsyncs the book from PG to the shelf
        """
        self.book = book

    def fetch(self):
        self.make_local_path()
        self.fetch_remote_book_to_local_path()

    def make_local_path(self):
        try:
            os.makedirs(self.book.local_path)
        except OSError:
            # FIXME logging.debug
            print("Folder {0} already exists".format(self.book.local_path))

    def fetch_remote_book_to_local_path(self):
        sh.rsync(
            '-rvhz',
            'ftp@ftp.ibiblio.org::gutenberg/{0}'.format(self.book.remote_path),
            self.book.local_path
        )
