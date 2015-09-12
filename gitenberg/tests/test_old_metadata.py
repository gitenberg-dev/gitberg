#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from gitenberg.book import Book
from gitenberg.util.catalog import BookMetadata


class TestBookMetadata(unittest.TestCase):

    def setUp(self):
        book = Book(1234)
        self.rdf_library = 'gitenberg/tests/test_data'
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
