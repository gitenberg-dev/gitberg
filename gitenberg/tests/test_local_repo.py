#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import unittest

import git

from gitenberg.local_repo import LocalRepo


class TestLocalRepo(unittest.TestCase):
    relative_test_repo_path = './gitenberg/tests/test_data/test_repo'

    def setUp(self):
        git.Repo.init(self.relative_test_repo_path)
        self.local_repo = LocalRepo(self.relative_test_repo_path)

    def tearDown(self):
        shutil.rmtree(self.relative_test_repo_path)

    def _touch_file(self, name):
        path = os.path.join(self.relative_test_repo_path, name)
        with open(path, 'a'):
            os.utime(path, None)

    def test_add_file(self):
        # If we create a file in a repo, and add it to the stage
        # is it listed in the representation of the index/stage
        self._touch_file('foof')
        self.local_repo.add_file('foof')
        self.assertEqual(
            self.local_repo.git.index.entries.keys(),
            [(u'foof', 0)]
        )

    def test_add_all_files(self):
        map(self._touch_file, ['foof', 'offo.txt', 'fofo.md'])
        self.local_repo.add_all_files()
        self.assertEqual(
            self.local_repo.git.index.entries.keys(),
            [(u'fofo.md', 0), (u'offo.txt', 0), (u'foof', 0)]
        )

    def test_add_all_files_filters_ignore_list(self):
        map(self._touch_file, ['offo.txt', 'fofo.ogg', 'zoom'])
        self.local_repo.add_all_files()
        self.assertEqual(
            self.local_repo.git.index.entries.keys(),
            [(u'offo.txt', 0), (u'zoom', 0)]
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
        
    def test_file_checks(self):
        self.assertFalse(self.local_repo.metadata_file)

