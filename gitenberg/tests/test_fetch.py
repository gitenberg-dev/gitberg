#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from gitenberg.book import Book
from gitenberg.fetch import BookFetcher
from gitenberg import config

class TestBookFetcher(unittest.TestCase):

    def setUp(self):
        self.book = Book(1283)
        self.fetcher = BookFetcher(self.book)

    def test_make_local_path(self):
        # creates a folder in the specified test dir
        self.fetcher.make_local_path()
        self.assertTrue(os.path.exists(config.data['library_path']+'/1283'))

    def test_remote_fetch(self):
        self.fetcher.fetch_remote_book_to_local_path()
        self.assertTrue(os.path.exists(config.data['library_path']+'/1283/1283.txt'))

    def tearDown(self):
        self.book.remove()
