#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

import sh

from gitenberg.book import Book
from gitenberg.local_repo import LocalRepo
from gitenberg import config



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
