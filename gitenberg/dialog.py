#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A collection of tools for interactive commandline dialogs
"""

from appdirs import user_data_dir
from six.moves import input
from getpass import getpass

class ConfigGenerator(object):
    def __init__(self, current={}):
        """ Asks questions of the user and
        generates a config file with necessary data for gitberg
        with the responses.
        `.answers` contains responses suitable for saving into a config
        """
        self.answers = {}
        self.current = current
        if not self.current.get('library_path', ''):
            current['library_path']= user_data_dir('gitberg', 'Free Ebook Foundation')

    def ask_generic(self, key, prompt, pwd = False):
        if pwd:
            answer = getpass( prompt )
        else:
            if self.current.get(key,None):
                prompt = '{} [{}] >'.format(prompt, self.current.get(key,None))
            else:
                prompt = '{} >'.format(prompt)
            answer = input( prompt )
        self.answers[key] = answer if answer else self.current.get(key,None)

    def ask_username(self):
        self.ask_generic('gh_user', "What is your GitHub username?")

    def ask_email(self):
        self.ask_generic('gh_email', "What is your GitHub email?")

    def ask_rdf_library(self):
        self.ask_generic('rdf_library', "What is the path to your PG RDF library?")

    def ask_password(self):
        self.ask_generic('gh_password',
            "What is the GitHub password for the {0} user?".format(
                self.answers.get('gh_user','[not set]')
            ), pwd=True
        )

    def ask_library(self):
        self.ask_generic( 'library_path', "What is the path to the folder where you would like to store books?")

    def ask(self):
        self.ask_library()
        self.ask_username()
        self.ask_email()
        if self.answers['gh_user']:
            self.ask_password()
        self.ask_rdf_library()
