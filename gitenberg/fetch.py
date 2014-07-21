#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetches a folder of book files from a remote to local
"""

from __future__ import print_function
import os

MIRRORS = {}

LIBRARY_PATH = './library'


def make_directory_for_book(book_id, library_path=LIBRARY_PATH):
    book_path = "{0}/{1}".format(library_path, book_id)
    try:
        os.makedirs(book_path)
    except OSError:
        print("Folder {0} already exists".format(book_path))


def fetch(book_id):
    """ Fetches a book by book_id from a default remote """

    print("running fetch command")
    make_directory_for_book(book_id)
