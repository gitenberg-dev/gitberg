#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submodule which holds workflow methods
"""
from __future__ import print_function
import logging
import requests

from .book import Book
from . import actions

logger = logging.getLogger(__name__)

# extend this to all repos when ready
REPOS_LIST_URL = "https://raw.githubusercontent.com/gitenberg-dev/Second-Folio/master/list_of_repos.txt"

def upload_all_books(book_id_start, book_id_end, rdf_library=None):
    """ Uses the fetch, make, push subcommands to
        mirror Project Gutenberg to a github3 api
    """

    # TODO refactor appname into variable
    logger.info(
        "starting a gitberg mass upload: {0} -> {1}".format(
            book_id_start, book_id_end
        )
    )

    for book_id in range(int(book_id_start), int(book_id_end) + 1):
        errors = 0
        try:
            upload_book(book_id, rdf_library=rdf_library)
        except Exception as e:
            print(u'error\t{}'.format(book_id))
            logger.error(u"Error processing: {}\r{}".format(book_id, e))
            errors += 1
            if errors > 10:
                print('error limit reached!')
                break

def upload_list(book_id_list, rdf_library=None):
    """ Uses the fetch, make, push subcommands to add a list of pg books
    """
    with open(book_id_list, 'r') as f:
        for book_id in f:
            try:
                upload_book(book_id.strip(), rdf_library=rdf_library)
            except Exception as e:
                print(u'error\t{}'.format(book_id.strip()))
                logger.error(u"Error processing: {}\r{}".format(book_id.strip(), e))


def upload_book(book_id, rdf_library=None):
    logger.info("--> Beginning {0}".format(book_id))
    book = Book(book_id, rdf_library=rdf_library)
    book.all()

def apply_file(action, book_id_file, limit=10):
    book_list = []
    with open(book_id_file, 'r') as f:
        for line in f:
            book_list.append(line.strip())
    book_list = book_list[:limit] if limit else book_list
    apply_list(action, book_list)

def apply_all(action, book_id_start, book_id_end):
    book_list = range(int(book_id_start), int(book_id_end) + 1)
    apply_list(action, book_list)

def apply_list(arg_action, id_list):
    action = getattr(actions, arg_action)
    for book_id in id_list:
        try:
            book = action(book_id)
            print(u'{}\t{}'.format(arg_action, book_id))
            book.remove()
        except Exception as e:
            print(u'error\t{}'.format(book_id))
            logger.error(u"Error processing: {}\r{}".format(book_id, e))


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

try:
    all_repos = requests.get(REPOS_LIST_URL).content.strip().split("\n")
except requests.ConnectionError:
    all_repos = []
