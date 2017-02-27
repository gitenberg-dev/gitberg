#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch

from gitenberg.library import GitbergLibraryManager

# TODO Mock parsed config for library path with clever dict

class TestLibraryManager(unittest.TestCase):
    def setUp(self):
        self.library_path = 'path/to/library/'
        self.glm = GitbergLibraryManager()
        self.glm.config.data = {
            'library_path': self.library_path
        }

    def test_book_directories(self):
        with patch('os.listdir', return_value=[1, 2, 3, 4]) as _mock:
            self.glm.book_directories()
            _mock.assert_called_with(self.library_path)
