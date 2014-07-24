#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities for finding the paths to books remotely and locally
"""

# local path to the library directory
LIBRARY_PATH = './library'


class CantPathHereException(Exception):
    pass


def path_to_pg_book(book_id):
    """ turns an ebook_id into a string of paths
        this is the way PG organizes their folder paths
          4443  -> 4/4/4/4443/
    """
    if book_id < 10:
        raise CantPathHereException
    path = ''
    for digit in str(book_id)[:-1]:
        path = path + '{0}/'.format(digit)
    path = path + '{0}/'.format(str(book_id))
    return path


def path_to_library_book(book_id):
    return '{0}/{1}'.format(LIBRARY_PATH, book_id)
