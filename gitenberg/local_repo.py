#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os

import git
import sh

from .util.catalog import CdContext
from .util.filetypes import IGNORE_FILES

class LocalRepo(object):
    def __init__(self, book):
        self.book = book

    def add_file(self, filename):
        filetype = os.path.splitext(filename)[1]
        if filetype not in IGNORE_FILES:
            sh.git('add', filename)

    def add_all_files(self):
        with CdContext(self.book.local_path):
            sh.git.init('.')

            logging.debug("files to add: " + str(sh.ls()))

            # NOTE: repo.untracked_files is unreliable with CdContext
            # using sh.ls() instead, this doesn't recognize .gitignore
            for _file in sh.ls():
                for _subpath in _file.split():
                    logging.debug("adding file: " + str(_file))

                    self.add_file(_subpath)

    def commit(self, message):
        with CdContext(self.book.local_path):
            try:
                # note the double quotes around the message
                sh.git(
                    'commit',
                    '-m',
                    '"{message}"'.format(message=message)
                )
            except sh.ErrorReturnCode_1:
                print("Commit aborted for {0} with msg {1}".format(self.book.book_id, message))


class LocalBookRepo(object):
    """ A class for interacting with a git repo """

    def __init__(self, repo_path):
        """ takes a path to a git repo """
        self.repo_path = repo_path
        self.git = git.Repo(self.repo_path)

    def add_file(self, path):
        """ Takes <str> relative path from repo to file
        and adds it to the git repo index (stage) """
        self.git.index.add([path])

    def add_all_files(self):
        self.git.index.add(self.git.untracked_files)

    def commit(self, message):
        # TODO: emit warning if message is too long
        # FIXME: this likely relies on system env vars for git author
        self.git.index.commit(message)
