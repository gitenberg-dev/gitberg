#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A collection of tools for interactive commandline dialogs
"""

from appdirs import user_data_dir
from six.moves import input

class ConfigGenerator(object):
    def __init__(self):
        """ Generates a config file with nessisary data for giberg
        """
        self._data_dir = user_data_dir('gitberg', 'Free Ebook Foundation')
        self.answers = {}

    def ask_username(self):
        self.answers['gh_user'] = input("What is your GitHub username? [optional] >  ")

    def ask_password(self):
        self.answers['gh_password'] = input(
            "What is your GitHub password for the {0} user? [optional] >  ".format(
                self.answers['gh_user']
            )
        )

    def ask_library(self):
        # Suggest the standard data dir for user's OS
        self._ask_library_answer = input(
            """
            What is the path to the folder where you would like to store books?
            [{0}] >
            """.format(self._data_dir)
        )

        # The default answer should be the standard
        if not self._ask_library_answer:
            self._ask_library_answer = self._data_dir

        # FIXME: Check and ensure that the full dir path to the folder is
        # created and that nothing is overwritten by doing so
        self.answers['library_path'] = self._data_dir

    def ask(self):
        self.ask_library()
        self.ask_username()
        if self.answers['gh_user']:
            self.ask_password()
