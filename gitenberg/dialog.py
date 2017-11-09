#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" A collection of tools for interactive commandline dialogs
"""

import os
import wget
import tarfile

from appdirs import user_data_dir
from six.moves import input
from getpass import getpass
from .util import util

# gutenberg RDF link mirror
RDF_URL = "http://gutenberg.readingroo.ms/cache/generated/feeds/rdf-files.tar.bz2"

class ConfigGenerator(object):
    def __init__(self, current={}):
        """ Generates a config file with necessary data for gitberg
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
        self.ask_generic('gh_email',"What is your GitHub email?")

    def ask_rdf_library(self):

        # Ensure we get a y/n answer
        shouldDownload = None
        while shouldDownload == None:
            answer = input("Do you have a local PG RDF library [Y/n]")
            if answer == "y" or answer == "Y" or answer == "":
                shouldDownload = False
            elif answer == "n" or answer == "N":
                shouldDownload = True
            
        if shouldDownload:
            self.ask_generic('rdf_library',"What is the path to the directory where you would like to have the PG RDF library? (This is a >= 1.1GB file)")
            if not os.path.exists(self.answers['rdf_library']):
                os.makedirs(self.answers['rdf_library'])
            with util.cd(self.answers['rdf_library']):   
                bz2_rdf = wget.download(RDF_URL)
                with tarfile.open(bz2_rdf, 'r:bz2') as out:
                    out.extractall()
        else:
            self.ask_generic('rdf_library',"What is the path to your PG RDF library?")
            
    def ask_password(self):
        self.ask_generic('gh_password',
            "What is the GitHub password for the {0} user?".format(
                self.answers.get('gh_user','[not set]')
            ), pwd=True
        )

    def ask_library(self):
        # Suggest the standard data dir for user's OS
        self.ask_generic( 'library_path', "What is the path to the folder where you would like to store books?")
        # FIXME: Check and ensure that the full dir path to the folder is
        # created and that nothing is overwritten by doing so

    def ask(self):
        self.ask_library()
        self.ask_username()
        self.ask_email()
        if self.answers['gh_user']:
            self.ask_password()
        self.ask_rdf_library()
