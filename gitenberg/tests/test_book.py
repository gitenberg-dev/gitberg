#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from gitenberg.book import Book


class TestBookPath(unittest.TestCase):

    def setUp(self):
        self.book = Book(3456)

    def test_remote_path(self):
        self.assertEqual(
            self.book.remote_path,
            "3/4/5/3456/"
        )

    def test_local_path(self):
        self.assertTrue(
            self.book.local_path.endswith("/3456")
        )


class TestBookPathSubTen(unittest.TestCase):

    def setUp(self):
        self.book = Book(7)

    def test_path_to_pg(self):
        self.assertEqual(
            self.book.remote_path,
            "7/"
        )
