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
    def __init__(self):
        # by default, loads the default config location
        self.config = config.ConfigFile()

    @property
    def library_base_path(self):
        """ returns the path where library books are stored """
        return self.config.data['library_path']

    def book_directories(self):
        """ Returns a list of book directories in the library folder """
        return os.listdir(self.library_base_path)


def main():
    # FIXME: stupid simple implementation of library status
    glm = GitbergLibraryManager()
    for folder in glm.book_directories():
        print(folder)
