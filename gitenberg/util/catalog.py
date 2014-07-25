#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
import re
import sh

# sourced from http://www.gutenberg.org/MIRRORS.ALL
MIRRORS = {'default': 'ftp://ftp.ibiblio.org/pub/docs/books/gutenberg/'}


class CdContext():
    """ A context manager using `sh` to cd to a directory and back
        `with CdContext(new path to go to)`
    """

    def __init__(self, path):
        self._og_directory = str(sh.pwd()).strip('\n')
        self._dest_directory = path

    def __enter__(self):
        sh.cd(self._dest_directory)

    def __exit__(self, exception_type, exception_value, traceback):
        sh.cd(self._og_directory)


class BookMetadata():

    HTML_REGEX = re.compile('<[^<]+?>')

    def __init__(self, book, rdf_library='./rdf_library'):
        self.book = book
        self.rdf_path = "{0}/{1}/pg{1}.rdf".format(
            rdf_library, self.book.book_id
        )
        self.parse_rdf()

    def parse_rdf(self):
        """ cat|grep's the rdf file for minimum metadata
        """
        # FIXME: make this an rdf parser if I can
        _title = sh.grep(sh.cat(self.rdf_path), 'dcterms:title', _tty_out=False)
        try:
            _author = sh.grep(sh.cat(self.rdf_path), 'name', _tty_out=False)
            self.author = self._clean_properties(_author)
        except sh.ErrorReturnCode_1:
            self.author = "Various"

        self.title = self._clean_properties(_title)

    def _clean_properties(self, prop):
        if isinstance(prop, list):
            prop = [self._clean_prop(text) for text in prop]
        else:
            prop = self._clean_prop(prop)
        return prop

    def _clean_prop(self, prop):
        prop = unicode(prop)
        prop = self.HTML_REGEX.sub('', prop)
        prop = prop.replace('\n', '')
        prop = ' '.join(prop.split())
        return prop
