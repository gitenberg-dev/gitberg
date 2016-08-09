#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest

import git
import sh

from gitenberg.book import Book
from gitenberg.local_repo import LocalRepo
from gitenberg.local_repo import LocalBookRepo
from gitenberg import config

def null():
    pass

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

class TestLocalBookRepo(unittest.TestCase):
    relative_test_repo_path = './gitenberg/tests/test_data/test_repo'

    def setUp(self):
        git.Repo.init(self.relative_test_repo_path)
        self.local_repo = LocalBookRepo(self.relative_test_repo_path)

    def tearDown(self):
        shutil.rmtree(self.relative_test_repo_path)

    def test_add_file(self):
        # If we create a file in a repo, and add it to the stage
        # is it listed in the representation of the index/stage
        self._touch_file('foof')
        self.local_repo.add_file('foof')
        self.assertEqual(
            self.local_repo.git.index.entries.keys(),
            [(u'foof', 0)]
        )

    def test_add_files(self):
        files_list = ['foof', 'offo.txt', 'fofo.md']
        map(self._touch_file, files_list)
        self.local_repo.add_all_files()
        self.assertEqual(
            self.local_repo.git.index.entries.keys(),
            [(u'fofo.md', 0), (u'offo.txt', 0), (u'foof', 0)]
        )

    def test_commit(self):
        file_name = 'foom.txt'
        message = 'this is a commit messaage'
        self._touch_file(file_name)
        self.local_repo.add_file(file_name)
        self.local_repo.commit(message)

        latest_commit = self.local_repo.git.heads.master.commit
        self.assertEqual(
            latest_commit.message,
            message
        )


    def _touch_file(self, name):
        path = os.path.join(self.relative_test_repo_path, name)
        with open(path, 'a'):
            os.utime(path, None)
