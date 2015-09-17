#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A module to manage a collection of git book repos
"""
import os

from .config import ConfigFile

class GitbergLibraryManager(object):
    """ A god object for managing a collection of Gitberg style books
    """
    def __init__(self, config=None):
        """ optionally takes an intialized and parsed ConfigFile instance
        """
        # by default, loads the default config location
        if not config:
            config = ConfigFile()
            config.parse()
        self.config = config

    def library_base_path(self):
        """ returns the path where library books are stored
        """
        return self.config.data['library_path']



def main():
    # FIXME: stupid simple implementation of library status
    config = ConfigFile()
    config.parse()
    library_dir = config.data['library_path']
    for folder in os.listdir(library_dir):
        print(folder)
