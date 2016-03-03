#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submodule which holds workflow methods
"""
import logging
import requests

from .book import Book

# extend this to all repos when ready
REPOS_LIST_URL = "https://raw.githubusercontent.com/gitenberg-dev/Second-Folio/master/list_of_repos.txt"

def upload_all_books(book_id_start, book_id_end, rdf_library=None):
    """ Uses the fetch, make, push subcommands to
        mirror Project Gutenberg to a github3 api
    """

    # TODO refactor appname into variable
    logging.info(
        "starting a gitberg mass upload: {0} -> {1}".format(
            book_id_start, book_id_end
        )
    )

    for book_id in xrange(int(book_id_start), int(book_id_end)):
        upload_book(book_id, rdf_library=rdf_library)

def upload_list(book_id_list, rdf_library=None):
    """ Uses the fetch, make, push subcommands to add a list of pg books
    """
    for book_id in book_id_list.split(','):
        upload_book(book_id, rdf_library=rdf_library)


def upload_book(book_id,rdf_library=None):
    logging.info("--> Beginning {0}".format(book_id))
    book = Book(book_id)

    try:
        book.parse_book_metadata(rdf_library)
    except:
        logging.error(u"Can't parse metadata for this book: {0}".format(book.book_id))
        return
    book.all()

def apply_to_repos(action, args=None, kwargs=None, repos=None):

    if repos is None:
        repos = all_repos
    
    if args is None:
        args = []
        
    if kwargs is None:
        kwargs = {}
        
    for repo in repos:
        try:
            result = action (repo, *args, **kwargs)
        except Exception as e:
            result = e
        yield result

all_repos = requests.get(REPOS_LIST_URL).content.strip().split("\n")
