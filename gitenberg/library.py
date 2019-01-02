#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A module to manage a collection of git book repos
"""
from __future__ import print_function
import os

from . import config
from .util.catalog import Rdfcache

class GitbergLibraryManager(object):
    """ A god object for managing a collection of Gitberg style books
    """
    def __init__(self):
        # by default, loads the default config location
        config.ConfigFile()

    def book_directories(self):
        """ Returns a list of book directories in the library folder """
        return os.listdir(config.data['library_path'])

    def update_rdf(self, force=False):
        rdf = Rdfcache(rdf_library=config.data['rdf_library'])
        rdf.download_rdf(force=force)

def main(force=False):
    glm = GitbergLibraryManager()
    numbooks = 0
    for folder in glm.book_directories():
        path = os.path.join(config.data['library_path'], folder)
        if os.path.isdir(path):
            numbooks += 1
    print("{} book repos in library".format(numbooks))
    rdf_good = not glm.update_rdf(force=force)
    if rdf_good:
        print("rdf library is up-to-date")
    else:
        print("rdf library could not be updated")
