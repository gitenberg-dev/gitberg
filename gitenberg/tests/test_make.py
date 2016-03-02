#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

import sh

from gitenberg.book import Book
from gitenberg.make import LocalRepo
from gitenberg import config


class TestLocalRepo(unittest.TestCase):

    def setUp(self):
        self.book = Book(13529)
        # TODO: Mock fetch_remote_book_to_local_path to
        #       copy test_data/sea_ppwer to 13529

        def copy_test_book():
            # FIXME: use filesystem for this, cp fails silently?
            sh.cp('./gitenberg/tests/test_data/1234', library_path)

        self.book.fetch_remote_book_to_local_path = copy_test_book
        self.book.fetch()

    def test_init(self):
        l_r = LocalRepo(self.book)
        self.assertEqual(
            l_r.book,
            self.book
        )

    def test_init_repo(self):
        l_r = LocalRepo(self.book)
        l_r.add_all_files()
        self.assertTrue(
            os.path.exists(config.data['library_path']+'/13529/.git')
        )

    def tearDown(self):
        self.book.remove()

def null():
    pass

# class TestNewFileHandler():

#     def setUp(self):
#         self.book = Book(333, library_path='./test/library')
#         self.book.parse_book_metadata(rdf_library=self.book.library_path)
#         self.book.fetch_remote_book_to_local_path = null
#         self.book.fetch()
#         self.file_handler = NewFilesHandler(self.book)

#     def test_readme(self):
#         self.file_handler.template_readme()

#         self.assertTrue(
#             os.path.exists('./test/library/333/README.rst')
#         )

#     def tearDown(self):
#         self.book.remove()
