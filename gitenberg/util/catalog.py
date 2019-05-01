#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""
import csv
import errno
import json
import logging
import os
import re
import shutil
import tarfile
import time

import dateutil.parser
import pytz
import requests

from .. import pg_wikipedia
from ..config import NotConfigured
from ..metadata.pandata import Pandata
from ..metadata.pg_rdf import pg_rdf_to_json, htm_modified
from ..parameters import GITHUB_ORG

RDF_URL = "https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2"
RDF_PATH = "/tmp/rdf.tar.bz2"
# 1 day
RDF_MAX_AGE = 60 * 60 * 24

# sourced from http://www.gutenberg.org/MIRRORS.ALL
MIRRORS = {'default': 'ftp://gutenberg.pglaf.org/mirrors/gutenberg/'}
utc = pytz.UTC

with open(os.path.join(
    os.path.dirname(__file__),
    '../data/gutenberg_descriptions.json'
)) as descfile:
    DESCS = json.load(descfile)

descs = {}
for desc in DESCS:
    descs[desc['identifier'][32:]] = desc['description']
repo_list = []
with open(os.path.join(os.path.dirname(__file__), '../data/GITenberg_repo_list.tsv')) as repofile:
    for row in csv.reader(repofile, delimiter='\t', quotechar='"'):
        repo_list.append(row)
repo_for_pgid = {int(pgid): value for (pgid, value) in repo_list}
last_pgid = repo_list[-1][0]

missing_list = []
with open(os.path.join(os.path.dirname(__file__), '../data/missing.tsv')) as missingfile:
    for row in csv.reader(missingfile, delimiter='\t', quotechar='"'):
        missing_list.append(row)
missing_pgid = {int(pgid): value for (pgid, reason, value) in missing_list}

def get_all_repo_names():
    """Yields the full names of all the book repositories."""
    for repo in repo_for_pgid.values():
        yield '%s/%s' % (GITHUB_ORG, repo)

def get_repo_name(repo_name):
    if re.match(r'^\d+$', repo_name):
        try:
            repo_name = repo_for_pgid[int(repo_name)]
        except KeyError:
            pass
    return repo_name

class NoRDFError(Exception):
    pass

class BookMetadata(Pandata):
    def __init__(self, book, rdf_library='./rdf_library', enrich=True, datafile=None):
        if datafile:
            super(BookMetadata, self).__init__(datafile=datafile)
            self.rdf_path = "{0}/{1}/pg{1}.rdf".format(
                book.rdf_library, book.book_id
            )
            return
        self.book = book
        try:
            assert os.path.exists(rdf_library)
        except Exception as e:
            raise NotConfigured(e)
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
            raise NoRDFError(e)

        if not self.authnames():
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

    def pg_modified(self):
        mod_str = htm_modified(self.rdf_path)
        return utc.localize(dateutil.parser.parse(mod_str))

class Rdfcache(object):
    downloading = False

    def __init__(self, rdf_library='./rdf_library'):
        if rdf_library.endswith('/cache/epub'):
            # because unzipping the archive creates ./cache/epub
            self.rdf_library_dir = rdf_library[0:-11]
        else:
            self.rdf_library_dir = rdf_library

    def download_rdf(self, force=False):
        """Ensures a fresh-enough RDF file is downloaded and extracted.

        Returns True on error."""
        if self.downloading:
            return True

        if not force and (os.path.exists(RDF_PATH) and
                (time.time() - os.path.getmtime(RDF_PATH)) < RDF_MAX_AGE):
            return False
        self.downloading = True
        logging.info('Re-downloading RDF library from %s' % RDF_URL)
        try:
            shutil.rmtree(os.path.join(self.rdf_library_dir, 'cache'))
        except OSError as e:
            # Ignore not finding the directory to remove.
            if e.errno != errno.ENOENT:
                raise

        try:
            with open(RDF_PATH, 'w') as f:
                with requests.get(RDF_URL, stream=True) as r:
                    shutil.copyfileobj(r.raw, f)
        except requests.exceptions.RequestException as e:
            logging.error(e)
            return True

        try:
            with tarfile.open(RDF_PATH, 'r') as f:
                f.extractall(self.rdf_library_dir)
        except tarfile.TarError as e:
            logging.error(e)
            try:
                os.unlink(RDF_PATH)
            except:
                pass
            return True
        self.downloading = False
        return False

    def get_repos_to_upload(self):
        pg_id = int(last_pgid) + 1
        more = True
        pg_ids = []
        while more:
            new_rdffile = os.path.join(
                self.rdf_library_dir,
                'cache',
                'epub',
                unicode(pg_id),
                'pg{}.rdf'.format(pg_id)
            )
            if os.path.exists(new_rdffile):
                pg_ids.append(pg_id)
                pg_id += 1
            else:
                if pg_id in missing_pgid:
                    pg_id += 1
                else:
                    more = False
        return pg_ids
