#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
import csv
import json
import os
import re

from gitenberg import pg_wikipedia
from gitenberg.config import NotConfigured
from gitenberg.metadata.pandata import Pandata
from gitenberg.metadata.pg_rdf import pg_rdf_to_json

# sourced from http://www.gutenberg.org/MIRRORS.ALL
MIRRORS = {'default': 'ftp://gutenberg.pglaf.org/mirrors/gutenberg/'}

with open(os.path.join(os.path.dirname(__file__), '../data/gutenberg_descriptions.json')) as descfile:
    DESCS = json.load(descfile)

descs = {}
for desc in DESCS:
    descs[desc['identifier'][32:]] = desc['description']
repo_list = []
with open(os.path.join(os.path.dirname(__file__), '../data/GITenberg_repo_list.tsv')) as repofile:
    for row in csv.reader(repofile, delimiter='\t', quotechar='"'):
        repo_list.append(row)
repo_for_pgid = {int(pgid): value for (pgid, value) in repo_list}

def get_repo_name(repo_name):
    if re.match( r'\d+', repo_name):
        repo_name = repo_for_pgid[int(repo_name)]
    return repo_name

class CdContext():
    """ A context manager using `os` to cd to a directory and back
        `with CdContext(new path to go to)`
    """

    def __init__(self, path):
        self._og_directory = str(os.getcwd()).strip('\n')

        self._dest_directory = path

    def __enter__(self):
        os.chdir(self._dest_directory)

    def __exit__(self, exception_type, exception_value, traceback):
        os.chdir(self._og_directory)


class BookMetadata(Pandata):
    def __init__(self, book, rdf_library='./rdf_library', enrich=True):
        self.book = book
        self.rdf_path = "{0}/{1}/pg{1}.rdf".format(
            rdf_library, self.book.book_id
        )
        self.parse_rdf()
        if enrich:
            self.enrich()

    def parse_rdf(self):
        """ Parses the relevant PG rdf file
        """
        try:
            self.metadata = pg_rdf_to_json(self.rdf_path)
        except IOError as e:
            raise NotConfigured(e)

        if len(self.authnames()) == 0:
            self.author = ''
        elif len(self.authnames()) == 1:
            self.author = self.authnames()[0]
        else:
            self.author = "Various"

    def enrich(self):
        description = pg_wikipedia.get_pg_summary(self.book.book_id)
        if not description:
            description = descs.get(self.book.book_id, '')
        else:
            description = description + '\n From Wikipedia (CC BY-SA).'
            self.identifiers.update({'wikidata': pg_wikipedia.get_wd_id(self.book.book_id)})
            self.metadata['wikipedia'] = pg_wikipedia.get_pg_links(self.book.book_id)
        if not description:
            description = self.description
        self.metadata['description'] = description
