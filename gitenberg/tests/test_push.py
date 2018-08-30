#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

import gitenberg
from gitenberg.book import Book
from gitenberg.make import NewFilesHandler
from gitenberg.local_repo import LocalRepo

from mock import patch


class TestNewFileHandler(unittest.TestCase):

    def setUp(self):
        def here(appname):
            return os.path.join(os.path.dirname(__file__),'test_data')
        with patch.object(gitenberg.config.appdirs, 'user_config_dir', here) as path:
            with patch('github3.login') as login:
                self.login = login
                self.book = Book(1234)
        self.book.local_repo = LocalRepo(os.path.join(os.path.dirname(__file__),'test_data/1234'))
        self.book.parse_book_metadata()
        self.file_maker = NewFilesHandler(self.book)

    def tearDown(self):
        pass