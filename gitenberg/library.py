#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A module to manage a collection of git book repos
"""
from __future__ import print_function
import os

from . import config

class GitbergLibraryManager(object):
    """ A god object for managing a collection of Gitberg style books
    """
    def __init__(self):
        # by default, loads the default config location
        self.config = config.ConfigFile()

    def book_directories(self):
        """ Returns a list of book directories in the library folder """
        return os.listdir(config.data['library_path'])


def main():
    # FIXME: stupid simple implementation of library status
    glm = GitbergLibraryManager()
    for folder in glm.book_directories():
        print(folder)
