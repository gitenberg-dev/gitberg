#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
import re
import sh

# sourced from http://www.gutenberg.org/MIRRORS.ALL
MIRRORS = {'default': 'ftp://ftp.ibiblio.org/pub/docs/books/gutenberg/'}


class EbookRecord():

    RDF_LIBRARY = './rdf_library'

    def __init__(self, book_id):
        self.book_id = book_id
        rdf_path = "{0}/{1}/pg{1}.rdf".format(self.RDF_LIBRARY, book_id)
        self._parse_rdf(rdf_path)

    def _parse_rdf(self, rdf_path):
        """ cat|grep's the rdf file for minimum metadata
        """
        # FIXME: make this an rdf parser if I can
        _title = sh.grep(sh.cat(rdf_path), 'dcterms:title', _tty_out=False)
        _author = sh.grep(sh.cat(rdf_path), 'name', _tty_out=False)

        self.title = self._clean_properties(_title)
        self.author = self._clean_properties(_author)

    def _clean_properties(self, prop):
        if isinstance(prop, list):
            prop = [self._clean_prop(text) for text in prop]
        else:
            prop = self._clean_prop(prop)
        return prop

    def _clean_prop(self, prop):
        HTML_REGEX = '<[^<]+?>'
        prop = str(prop)
        prop = re.sub(HTML_REGEX, '', prop)
        prop = prop.replace('\n', '')
        prop = ' '.join(prop.split())
        return prop
