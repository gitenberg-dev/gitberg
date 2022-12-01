#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syncs a local git book repo to a remote git repo (by default, github)
"""

import logging
import re

import git
import github3
import semver

from . import config
from .parameters import GITHUB_ORG, ORG_HOMEPAGE

logger = logging.getLogger(__name__)

class GithubRepo():

    def __init__(self, book):
        self.org_name = GITHUB_ORG
        self.org_homepage = ORG_HOMEPAGE
        self.book = book
        self.repo = None
        if not config.data:
            config.ConfigFile()
        self.create_api_handler()

    @property
    def repo_id(self):
        return "{}/{}".format(self.org_name, self.book.meta._repo)

    def push(self):
        self.book.local_repo.git.remote('origin').push(
            self.book.local_repo.git.refs.master, tags=True
        )

    def create_and_push(self):
        self.create_repo()
        origin = self.add_remote_origin_to_local_repo()
        origin.push(self.book.local_repo.git.refs.master)

    def update(self, message):
        self.book.local_repo.update(message)
        self.push()

    def tag(self, version, message=''):
        if version == "bump" or not version:
            old_version = self.book.meta._version
            if old_version:
                version = old_version
            else:
                version = '0.0.1'
        while version in self.book.local_repo.git.tags:
            version = semver.bump_patch(version)
        self.book.meta.metadata['_version'] = version
        self.book.save_meta()
        self.update('tag: {}. {}'.format(version, message))
        ref = self.book.local_repo.tag(version)
        self.push()
        logger.info("tagged and pushed %s" % str(ref))


    def create_api_handler(self):
        """ Creates an api handler and sets it on self """
        try:
            if 'gh_access_token' in config.data:
                self.github = github3.login(token=config.data['gh_access_token'])
            else:
                self.github = github3.login(username=config.data['gh_user'],
                                            password=config.data['gh_password'])
            remaining = self.github.ratelimit_remaining
            logger.info("ratelimit remaining: %s" % remaining)
        except KeyError as e:
            raise config.NotConfigured(e)
        if hasattr(self.github, 'set_user_agent'):
            self.github.set_user_agent('{}: {}'.format(self.org_name, self.org_homepage))
        try:
            self.org = self.github.organization(self.org_name)
        except github3.GitHubError:
            logger.error("Possibly the github ratelimit has been exceeded")
            logger.info("ratelimit: %s" % str(self.github.ratelimit_remaining))

    def format_desc(self):
        if hasattr(self.book, 'meta'):
            title = re.sub(r'[\r\n \t]+', ' ', self.book.meta.title)
            author = ' by {}'.format(self.book.meta.authors_short())
        else:
            title = self.book.repo_name
            author = ''

        # total length < 255
        excess = len(title) + len(author) - 212
        if excess > 0:
            title = title[0:- excess] + '…'
        return u'{0}{1} is a Project Gutenberg book, now on Github.'.format(title, author)

    def create_repo(self):
        try:
            self.repo = self.org.create_repository(
                self.book.repo_name,
                description=self.format_desc(),
                homepage=self.org_homepage,
                private=False,
                has_issues=True,
                has_wiki=False
            )
        except github3.GitHubError as e:
            logger.warning("repo already created?: %s" % e)
            self.repo = self.github.repository(self.org_name, self.book.repo_name)

    def update_repo(self):
        try:
            self.repo = self.github.repository(self.org_name, self.book.repo_name)
            self.repo.edit(
                self.book.repo_name,
                description=self.format_desc(),
                homepage=self.org_homepage,
                private=False,
                has_issues=True,
                has_wiki=False,
                has_downloads=True
            )
        except github3.GitHubError as e:
            logger.warning("couldn't edit repo: %s" % e)

    def add_remote_origin_to_local_repo(self):
        try:
            origin = self.book.local_repo.git.create_remote('origin', self.repo.ssh_url)
        except git.exc.GitCommandError as e:
            logger.warning("We may have already added a remote origin to this repo")
            return self.book.local_repo.git.remote('origin')
        return origin
