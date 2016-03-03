#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syncs a local git book repo to a remote git repo (by default, github)
"""

from __future__ import print_function
import logging
import time

import github3
import sh

from .util.catalog import CdContext
from . import config


class GithubRepo():

    def __init__(self, book):
        self.org_name = 'GITenberg'
        self.org_homepage = u'https://www.GITenberg.org/'
        self.book = book
        if not config.data:
            config.ConfigFile()
        self.create_api_handler()

    def create_and_push(self):
        self.create_repo()
        self.add_remote_origin_to_local_repo()
        self.push_to_github()

    def create_api_handler(self):
        """ Creates an api handler and sets it on self """
        if not config.data:
            raise config.NotConfigured
        try:
            self.github = github3.login(username=config.data['gh_user'],
                                    password=config.data['gh_password'])
        except KeyError as e:
            raise config.NotConfigured(e)
        if hasattr(self.github, 'set_user_agent'):
            self.github.set_user_agent('{}: {}'.format(self.org_name, self.org_homepage))
        self.org = self.github.organization(login=self.org_name)
        logging.info("ratelimit: " + str(self.org.ratelimit_remaining))

    def format_desc(self):
        return u'{0} by {1}\n is a Project Gutenberg book, now on Github.'.format(
            self.book.meta.title, self.book.meta.author
        )


    def create_repo(self):
        try:
            self.repo = self.org.create_repo(
                self.book.meta._repo,
                # FIXME: Filter out 'control characters' arre not allowed in
                # desc github
                # description=self.format_desc(),
                homepage=self.org_homepage,
                private=False,
                has_issues=True,
                has_wiki=False,
                has_downloads=True
            )
        except github3.GitHubError as e:
            logging.warning(u"repo already created?: {}".format(e))
            self.repo = self.github.repository(self.org_name, self.book.meta._repo)

    def add_remote_origin_to_local_repo(self):
        with CdContext(self.book.local_path):
            try:
                sh.git('remote', 'add', 'origin', self.repo.ssh_url)
            except sh.ErrorReturnCode_128:
                print("We may have already added a remote origin to this repo")

    def push_to_github(self):
        with CdContext(self.book.local_path):
            try:
                sh.git.push('origin', 'master')
            except sh.ErrorReturnCode_128:
                logging.error(u"github repo not ready yet")
                time.sleep(10)
                sh.git('push', 'origin', 'master')
