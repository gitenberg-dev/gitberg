#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import git
import dateutil.parser

from .util.filetypes import IGNORE_FILES

logger = logging.getLogger(__name__)
img_exts = ('jpg', 'jpeg', 'png', 'gif')

class LocalRepo(object):
    """ A class for interacting with a git repo """
    def __init__(self, repo_path, cloned_repo=None):
        #wrap the cloned repo if it exists
        if cloned_repo:
            self.git = cloned_repo
            self.repo_path = self.git.working_dir
            return
        # Takes a path to a git repo
        self.repo_path = repo_path
        try:
            self.git = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            # uninitialized Repo
            self.git = git.Repo.init(self.repo_path)

    def add_file(self, path):
        # Takes <str> relative path from repo and stages it
        logger.debug(u'Staging this file: ' + str(self.git.untracked_files))
        self.git.index.add([path])

    def add_all_files(self):
        # Stages all untracked files
        untracked_files = [_file for _file in self.git.untracked_files
                           if os.path.splitext(_file)[-1] not in IGNORE_FILES]
        logger.debug(u'Staging the following files: ' + str(untracked_files))
        self.git.index.add(untracked_files)
        return len(untracked_files)

    def commit(self, message):
        # Creates a new git commit based on files in the stage with `message`<str>
        self.git.index.commit(message)

    def update(self, message):
        self.git.git.add(update=True)
        self.git.index.commit(message)

    def tag(self, version):
        return self.git.create_tag(version, message='bump version')
        
    def no_tags(self):
        for tag in self.git.tags:
            return False
        return True

    def mod_date(self, path):
        return dateutil.parser.parse(self.git.git.log('-1', '--format=%aI', '--', path))

    def cover_files(self):
        covers = []
        for root, dirs, files in os.walk(self.repo_path):
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            covers = covers + [os.path.join(root,f)[len(self.repo_path) + 1:] for f in files if (
                    'cover' in f and f.lower().split('.')[-1] in img_exts
                )]
        return covers

    @property
    def metadata_file(self):
        if self.repo_path and os.path.isfile(os.path.join(self.repo_path, 'metadata.yaml')):
            return os.path.join(self.repo_path, 'metadata.yaml')
        else:
            return None
