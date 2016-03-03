#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A module to manage a collection of git book repos
"""
import os

from . import config

class GitbergLibraryManager(object):
    """ A god object for managing a collection of Gitberg style books
    """
    def __init__(self, config=None):
        """ optionally takes an intialized and parsed ConfigFile instance
        """
        # by default, loads the default config location
        if not config.data:
            config.ConfigFile()

    def library_base_path(self):
        """ returns the path where library books are stored
        """
        return config.data['library_path']



def main():
    # FIXME: stupid simple implementation of library status
    config.ConfigFile()
    library_dir = config.data['library_path']
    for folder in os.listdir(library_dir):
        print(folder)
