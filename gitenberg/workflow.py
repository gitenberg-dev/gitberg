#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submodule which holds workflow methods
"""
from __future__ import print_function
import logging

from .book import Book
from . import actions
from .util.catalog import missing_pgid, Rdfcache

logger = logging.getLogger(__name__)

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
    if not book_id_end:
        book_id_end = book_id_start
    for book_id in range(int(book_id_start), int(book_id_end) + 1):
        cache = {}
        errors = 0
        try:
            if int(book_id) in missing_pgid:
                print(u'missing\t{}'.format(book_id))
                continue
            book_id, repo_name = upload_book(book_id, rdf_library=rdf_library, cache=cache)
            print("%s\t%s" % (book_id, repo_name))
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
        cache = {}
        for book_id in f:
            book_id = book_id.strip()
            try:
                if int(book_id) in missing_pgid:
                    print(u'missing\t{}'.format(book_id))
                    continue
                upload_book(book_id, rdf_library=rdf_library, cache=cache)
            except Exception as e:
                print(u'error\t{}'.format(book_id))
                logger.error(u"Error processing: {}\r{}".format(book_id, e))


def upload_book(book_id, rdf_library=None, cache={}):
    logger.info("--> Beginning {0}".format(book_id))
    book = Book(book_id, rdf_library=rdf_library, cache=cache)
    book.all()
    return (book_id, book.repo_name)

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
    cache = {}
    for book_id in id_list:
        try:
            if book_id in missing_pgid:
                print(u'missing\t{}'.format(book_id))
                continue
            book = action(book_id, cache=cache)
            print(u'{}\t{}'.format(arg_action, book_id))
            book.remove()
        except Exception as e:
            print(u'error\t{}'.format(book_id))
            logger.error(u"Error processing: {}\r{}".format(book_id, e))


def apply_to_repos(action, args=None, kwargs=None, repos=[]):

    if args is None:
        args = []

    if kwargs is None:
        kwargs = {}

    for repo in repos:
        try:
            result = action(repo, *args, **kwargs)
        except Exception as e:
            result = e
        yield result

def upload_new_books(rdf_library=None):
    rdf = Rdfcache(rdf_library=rdf_library)
    rdf.download_rdf()
    to_upload = rdf.get_repos_to_upload()
    cache = {}
    for book_id in to_upload:
        try:
            (pg_id, repo_name) = upload_book(book_id, rdf_library=rdf_library, cache=cache)
            print("{}\t{}".format(pg_id, repo_name))
        except Exception as e:
            print(u'error\t{}'.format(book_id))
            logger.error(u"Error processing: {}\r{}".format(book_id, e))
