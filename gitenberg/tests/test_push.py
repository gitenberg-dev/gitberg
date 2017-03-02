#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest

import gitenberg
from gitenberg.book import Book
from gitenberg.make import NewFilesHandler
from gitenberg.local_repo import LocalRepo

from mock import patch

mock_travis_response = {"key":"-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArzsEoY0bHoCHAFx3LhAk\nnIhc9WT3ovvv5El6U2KRWl/eo+IWR2QTNKjkMmA9uI8QGXlpy3aVu4gO/uDwmmZU\nmC/bGiXrsk0SUrg0pmkGBe2uStqcD4/lD3hLdVwPMhE5WgcxGL4XH4YT1x1jxGT3\n77ivznNZB0eSedUt3WDgySQTcHI+Wx35ip6oB2wljZqZ6rA+CfiJ+IgUltKEnQSo\naAroftbXT3M/9Z2mOc7HTLf7LNpsqwKR3iMqU98BC5Foj4ue2blAtQQ2BbSjNli+\neIUEE7irQc6J5h3IK5TIqo3unErBCGUaaZjKBXUy00sE2yatxbWa97+lujoAhlEs\naFTmm+mCrneK0cOujY2BWm3UuUyFrEiSYrFMfG/P+JLS1FGYLZHfZMRem8AUNcfN\nUz3spMwm4VRMBFSTOxxth3Wpk1TH4xfQ9ZCLGcojeixR/qYsuqzhNKM1ZtSE0ojp\nXATzLnzK6S9DmXA2SS+eSSiUbAlLsriEiWmAKMTgsFSpleHaRjZIZUICfZqKG/yf\nYFeOlbcwlKfU4COyu3EjbpgomeGp3arnkwqh6ppGrndQEb5ggzgbFopQp9SyxYm0\nGMJ+LN+0xpOsIJ7ClaM0QgFCB15XIQUU5jaNYEl+hPvxalEPD1sukoaGK4bpZkxa\nGtgiA1/fEQmfNoikRohCVScCAwEAAQ==\n-----END PUBLIC KEY-----\n","fingerprint":"12:75:cd:d4:13:6e:00:91:05:60:e2:69:9e:7b:a0:14"}

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

    def test_crypto(self):
        self.book.github_repo._repo_token = 'fake_repo_token'
        self.book.github_repo._travis_repo_public_key = mock_travis_response['key']
        
        key = self.book.github_repo.travis_key()
        self.assertTrue( len(key) == 684)
    

    def tearDown(self):
        pass