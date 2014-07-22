#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches a folder of book files from a remote to local
"""

from __future__ import print_function
import os

import sh

## Path functions
def path_to_pg_book(book_id):
    """ turns an ebook_id into a string of paths
        this is the way PG organizes their folder paths
          4443  -> 4/4/4/4443/
    """
    path = ''
    for digit in str(book_id)[:-1]:
        path = path + '{0}/'.format(digit)
    path = path + '{0}/'.format(str(book_id))
    return path


LIBRARY_PATH = './library'

class Book():

    def __init__(self, book_id, library_path=LIBRARY_PATH):
        """
        A Book:
          - has a shelf (folder in library directory)
          - has an `author`
          - has a `title`
        """
        self.book_id = book_id
        self.library_path = library_path

        self.make_shelf_in_library()
        self.rsync_files_from_remote()


    def make_shelf_in_library(self):
        self.book_path = "{0}/{1}".format(self.library_path, self.book_id)
        try:
            os.makedirs(self.book_path)
        except OSError:
            # FIXME logging.debug
            print("Folder {0} already exists".format(self.book_path))

    def rsync_files_from_remote(self):
        sh.rsync(
            '-rvhz',
            'ftp@ftp.ibiblio.org::gutenberg/{0}'.format(path_to_pg_book(self.book_id)),
            './{0}/{1}'.format( self.library_path, self.book_id )
        )




def fetch(book_id):
    # TODO: if make is passed, pass the ebook to make
    book = Book(book_id)
