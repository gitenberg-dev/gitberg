#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os

import git

from .util.filetypes import IGNORE_FILES

class LocalRepo(object):
    """ A class for interacting with a git repo """
    def __init__(self, repo_path):
        # Takes a path to a git repo
        self.repo_path = repo_path
        try:
            self.git = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            # uninitialized Repo
            self.git = git.Repo.init(self.repo_path)

    def add_file(self, path):
        # Takes <str> relative path from repo and stages it
        logging.debug(u'Staging this file: ' + str(self.git.untracked_files))
        self.git.index.add([path])

    def add_all_files(self):
        # Stages all untracked files
        untracked_files = [_file for _file in self.git.untracked_files
                           if os.path.splitext(_file)[-1] not in IGNORE_FILES]
        logging.debug(u'Staging the following files: ' + str(untracked_files))
        self.git.index.add(untracked_files)

    def commit(self, message):
        # Creates a new git commit based on files in the stage with `message`<str>
        self.git.index.commit(message)
