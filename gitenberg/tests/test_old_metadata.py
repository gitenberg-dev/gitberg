#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import MagicMock

from gitenberg.util.catalog import BookMetadata


class TestBookMetadata(unittest.TestCase):

    def setUp(self):
        mock_book = MagicMock()
        mock_book.book_id = 1234
        self.rdf_library = './gitenberg/tests/test_data/rdf_library'
        self.meta = BookMetadata(mock_book, rdf_library=self.rdf_library )

    def test_init(self):
        self.assertEqual(
            self.meta.rdf_path,
            '{0}/1234/pg1234.rdf'.format(self.rdf_library)
        )

    def test_parse_rdf(self):
        self.meta.parse_rdf()
        self.assertEqual(
            self.meta.agents("editor")[0]['agent_name'],
            u'Conant, James Bryant'
        )
        self.assertEqual(
            self.meta.title,
            u'Organic Syntheses\r\nAn Annual Publication of Satisfactory Methods for the Preparation of Organic Chemicals'
        )
