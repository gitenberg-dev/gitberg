#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import unittest

from mock import MagicMock
from mock import patch

from gitenberg.fetch import BookFetcher


class TestBookFetcher(unittest.TestCase):
    def setUp(self):
        # self.book = Book(1283)
        self.test_book_dir = './gitenberg/tests/test_data/test_book'
        self.remote_path = '1234/1234.txt'
        mock_book = MagicMock()
        mock_book.local_path = self.test_book_dir
        mock_book.remote_path = self.remote_path
        self.fetcher = BookFetcher(mock_book)

    @patch('os.makedirs')
    @patch('os.chmod')
    def test_make_local_path(self, mock_chmod, mock_makedirs):
        self.fetcher.make_local_path()
        mock_makedirs.assert_called_once_with(self.test_book_dir)
        mock_chmod.assert_called_once_with(self.test_book_dir, 0o777)

    @patch('sh.rsync')
    def test_remote_fetch(self, mock_rsync):
        self.fetcher.fetch_remote_book_to_local_path()
        mock_rsync.assert_called_once_with(
            '-rvhz',
            'ftp@gutenberg.pglaf.org::gutenberg/1234/1234.txt',
            self.test_book_dir + '/',
            '--exclude-from=exclude.txt'
        )
