#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches a folder of book files from a remote to local
"""

import os

import sh

from .parameters import PG_RSYNC

class BookFetcher():
    """ A BookFetcher:
        - makes a shelf (folder in library directory)
        - rsyncs the book from PG to the shelf
    """

    def __init__(self, book):
        self.book = book

    def fetch(self):
        self.fetch_remote_book_to_local_path()

    def fetch_remote_book_to_local_path(self):
        sh.rsync(
            '-rvhz',
            '{}{}'.format(PG_RSYNC, self.book.remote_path),
            self.book.local_path + '/',
            '--exclude-from=exclude.txt'
        )
