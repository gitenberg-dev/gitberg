#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Makes an organized git repo of a book folder
"""

import codecs
import os
from os.path import abspath, dirname

import git
import jinja2
import sh

from .util.catalog import CdContext
from .util.filetypes import IGNORE_FILES


class LocalRepo():

    def __init__(self, book):
        self.book = book

    def add_file(self, filename):
        filetype = os.path.splitext(filename)[1]
        if filetype not in IGNORE_FILES:
            sh.git('add', filename)

    def add_all_files(self):
        with CdContext(self.book.local_path):
            repo = git.Repo.init('./')
            for _file in repo.untracked_files:
                self.add_file(_file)

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
                print "Commit aborted for {0} with msg {1}".format(self.book.book_id, message)


class NewFilesHandler():
    """ NewFilesHandler - templates and copies additional files to book repos

    """
    README_FILENAME = 'README.rst'

    def __init__(self, book):
        self.book = book

        package_loader = jinja2.PackageLoader('gitenberg', 'templates')
        self.env = jinja2.Environment(loader=package_loader)

    def add_new_files(self):
        self.template_readme()
        self.copy_files()

    def template_readme(self):
        template = self.env.get_template('README.rst.j2')
        readme_text = template.render(
            title=self.book.meta.title,
            author=self.book.meta.author,
            book_id=self.book.book_id
        )
        #print type(self.meta.title), self.meta.title
        #print type(self.meta.author), self.meta.author

        readme_path = "{0}/{1}".format(
            self.book.local_path,
            self.README_FILENAME
        )
        with codecs.open(readme_path, 'w', 'utf-8') as readme_file:
            readme_file.write(readme_text)

    def copy_files(self):
        """ Copy the LICENSE and CONTRIBUTING files to each folder repo """
        files = [u'LICENSE', u'CONTRIBUTING.rst']
        this_dir = dirname(abspath(__file__))
        for _file in files:
            sh.cp(
                '{0}/templates/{1}'.format(this_dir, _file),
                '{0}/'.format(self.book_path)
            )


def make(book):

    # Initial commit of book files
    local_repo = LocalRepo(book)
    local_repo.add_all_files()
    local_repo.commit("Initial import from Project Gutenberg")

    # New files commit
    NewFilesHandler(book)

    local_repo.add_all_files()
    local_repo.commit("Adds Readme, contributing and license files to book repo")
