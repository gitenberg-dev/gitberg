#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syncs a local git book repo to a remote git repo (by default, github)
"""

from __future__ import print_function
import logging
from re import sub
import time

import github3
import sh

from .util.catalog import CdContext
try:
    from .secrets import GH_USER, GH_PASSWORD
except:
    print "no secrets file found, continuing without"


class GithubRepo():

    def __init__(self, book):
        self.book = book
        self.create_api_handler()

    def create_and_push(self):
        self.create_repo()
        self.add_remote_origin_to_local_repo()
        self.push_to_github()

    def create_api_handler(self):
        """ Creates an api handler and sets it on self """
        self.github = github3.login(username=GH_USER, password=GH_PASSWORD)
        if hasattr(self.github, 'set_user_agent'):
            self.github.set_user_agent('Project GITenberg: https://gitenberg.github.io/')
        self.org = self.github.organization(login='GITenberg')
        # FIXME: logging
        print("ratelimit: " + str(self.org.ratelimit_remaining))

    def format_desc(self):
        return u'{0} by {1}\n is a Project Gutenberg book, now on Github.'.format(
            self.book.meta.title, self.book.meta.author
        )

    def format_title(self):
        """ Takes a string and sanitizes it for Github's url name format """
        _title = sub("[ ',]+", '-', self.book.meta.title)
        title_length = 99 - len(str(self.book.book_id)) - 1
        if len(_title) > title_length:
            # if the title was shortened, replace the trailing _ with an ellipsis
            repo_title = "{0}__{1}".format(_title[:title_length], self.book.book_id)
        else:
            repo_title = "{0}_{1}".format(_title[:title_length], self.book.book_id)
        # FIXME: log debug, title creation
        print(len(repo_title), repo_title)
        return repo_title

    def create_repo(self):
        self.repo = self.org.create_repo(
            self.format_title(),
            description=self.format_desc(),
            homepage=u'https://GITenberg.github.io/',
            private=False,
            has_issues=True,
            has_wiki=False,
            has_downloads=True
        )

    def add_remote_origin_to_local_repo(self):
        with CdContext(self.book.local_path):
            try:
                sh.git('remote', 'add', 'origin', self.repo.ssh_url)
            except sh.ErrorReturnCode_128:
                print("We may have already added a remote origin to this repo")

    def push_to_github(self):
        with CdContext(self.book.local_path):
            try:
                sh.git('push', 'origin', 'master')
            except sh.ErrorReturnCode_128:
                logging.error(u"github repo not ready yet")
                time.sleep(10)
                sh.git('push', 'origin', 'master')
