#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

# from mock import MagicMock
import sh

from gitenberg.book import Book
from gitenberg.fetch import BookFetcher
from gitenberg.util.catalog import BookMetadata
from gitenberg.make import LocalRepo
from gitenberg.make import NewFilesHandler
from gitenberg.config import ConfigFile


def null():
    pass

class TestBookPath(unittest.TestCase):

    def setUp(self):
        self.book = Book(3456)

    def test_remote_path(self):
        self.assertEqual(
            self.book.remote_path,
            "3/4/5/3456/"
        )

    def test_local_path(self):
        self.assertEqual(
            self.book.local_path,
            "./library/3456"
        )


class TestBookPathSubTen(unittest.TestCase):

    def setUp(self):
        self.book = Book(7)

    def test_path_to_pg(self):
        self.assertEqual(
            self.book.remote_path,
            "7/"
        )


class TestBookFetcher(unittest.TestCase):

    def setUp(self):
        self.book = Book(1283, library_path='./test/library')
        self.fetcher = BookFetcher(self.book)

    def test_make_local_path(self):
        # creates a folder in the specified test dir
        self.fetcher.make_local_path()
        self.assertTrue(os.path.exists('./test/library/1283'))

    def test_remote_fetch(self):
        self.fetcher.fetch_remote_book_to_local_path()
        self.assertTrue(os.path.exists('./test/library/1283/1283.txt'))

    def tearDown(self):
        self.book.remove()


class TestBookMetadata(unittest.TestCase):

    def setUp(self):
        book = Book(1234)
        self.rdf_library = 'gitenberg/test_data'
        self.meta = BookMetadata(book, rdf_library=self.rdf_library)

    def test_init(self):
        self.assertEqual(
            self.meta.rdf_path,
            '{0}/1234/pg1234.rdf'.format(self.rdf_library)
        )

    def test_parse_rdf(self):
        self.meta.parse_rdf()
        self.assertEqual(
            self.meta.author,
            u'Conant, James Bryant'
        )
        self.assertEqual(
            self.meta.title,
            u'Organic Syntheses&#13;An Annual Publication of Satisfactory Methods for the Preparation of Organic Chemicals'
        )


class TestLocalRepo(unittest.TestCase):

    def setUp(self):
        library_path = './test/library'
        self.book = Book(13529, library_path=library_path)
        # TODO: Mock fetch_remote_book_to_local_path to
        #       copy test_data/sea_ppwer to 13529

        def copy_test_book():
            sh.cp('./gitenberg/test_data/13529', library_path)

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
            os.path.exists('./test/library/13529/.git')
        )

    def tearDown(self):
        self.book.remove()


class TestNewFileHandler():

    def setUp(self):
        self.book = Book(333, library_path='./test/library')
        self.book.fetch_remote_book_to_local_path = null
        self.book.fetch()
        self.file_handler = NewFilesHandler(self.book)

    def test_readme(self):
        self.file_handler.template_readme()
        self.assertTrue(
            os.path.exists('./test/library/333/README.rst')
        )

    def tearDown(self):
        self.book.remove()


class TestConfig(unittest.TestCase):
    def setUp(self):
        # TODO: mock?
        pass

    def test_init(self):
        cf = ConfigFile()
        self.assertEqual(
            cf.dir,
            os.path.expanduser('~/.config/gitberg')
        )


if __name__ == '__main__':
    unittest.main()
