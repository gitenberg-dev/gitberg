#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
submodule which holds workflow methods
"""
import logging

from .book import Book

def upload_all_books(book_id_start, book_id_end):
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
        logging.info("--> Beginning {0}".format(book_id))
        book = Book(book_id)

        # if '--rdf_library' in arguments:
        #     rdf_library = arguments['--rdf_library']
        # else:
        #     rdf_library = None

        # FIXME This was due to a very sketchy metadata parser based on grepping xml
        #       files and parsing single lines. It was failure prone, but it got me
        #       as far as making the github mirror of PG.
        #       Now that the metadata module exists, this should be rewritten
        try:
            book.parse_book_metadata()
        except:
            logging.error(u"Can't parse metadata for this book: {0}".format(book.book_id))
            continue
        book.all()
