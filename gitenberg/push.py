#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syncs a local git book repo to a remote git repo (by default, github)
"""

from re import sub

import github3
import sh

from .catalog import CdContext
from .catalog import EbookRecord
from .path import path_to_library_book
from .secrets import GH_USER, GH_PASSWORD


class GithubRepo():
    PROJECT_TEAM_ID = 211331

    def __init__(self, book):
        self.book = book
        self.create_api_handler()
        try:
            self.create_repo()
        except github3.GitHubError as g_exception:
            print g_exception
        self.book_path = path_to_library_book(self.book.book_id)
        self.add_remote_origin_to_local_repo()
        self.push_to_github()


    def create_api_handler(self):
        """ Creates an api handler and sets it on self """
        self.github = github3.login(username=GH_USER, password=GH_PASSWORD)
        if hasattr(self.github, 'set_user_agent'):
            self.github.set_user_agent('Project GITenberg: https://gitenberg.github.io/')
        self.org = self.github.organization(login='GITenberg')
        print "ratelimit: " + str(self.org.ratelimit_remaining)
        self.team = self.org.team(self.PROJECT_TEAM_ID)  # only one team in the github repo

    def format_desc(self):
        return u'%s by %s\n is a Project Gutenberg book, now on Github.' % (
            self.book.title, self.book.author
        )

    def format_title(self):
        """ Takes a string and sanitizes it for Github's url name format """
        _title = sub("[ ',]+", '-', self.book.title)
        title_length = 99 - len(str(self.book.book_id)) - 1
        if len(_title) > title_length:
            # if the title was shortened, replace the trailing _ with an ellipsis
            repo_title = "%s__%s" % (_title[:title_length], self.book.book_id)
        else:
            repo_title = "%s_%s" % (_title[:title_length], self.book.book_id)
        print len(repo_title), repo_title
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
        with CdContext(self.book_path):
            try:
                sh.git('remote', 'add', 'origin', self.repo.ssh_url)
            except sh.ErrorReturnCode_128:
                print "We may have already added a remote origin to this repo"

    def push_to_github(self):
        with CdContext(self.book_path):
            sh.git('push', 'origin', 'master')

def push(book_id):
    book = EbookRecord(book_id)
    GithubRepo(book)
