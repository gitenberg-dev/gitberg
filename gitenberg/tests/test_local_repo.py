#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

import sh

from gitenberg.book import Book
from gitenberg.local_repo import LocalRepo
from gitenberg import config


class TestLocalRepo(unittest.TestCase):

    def setUp(self):
        self.book = Book(13529)
        # TODO: Mock fetch_remote_book_to_local_path to
        #       copy test_data/sea_ppwer to 13529
        self.library_path = './test/library'

        def copy_test_book():
            # FIXME: use filesystem for this, cp fails silently?
            sh.cp('./gitenberg/tests/test_data/1234', config.data['library_path'])

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
