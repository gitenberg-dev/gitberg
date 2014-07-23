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

from .catalog import EbookRecord
from .filetypes import IGNORE_FILES
from .path import path_to_library_book


# TODO:
# --make repo
# --add files to repo
# initial commit
# template files into repo dir
# add those templated files on 2nd commit


class CdContext():
    """ A context manager using `sh` to cd to a directory and back
        `with CdContext(new path to go to)`
    """

    def __init__(self, path):
        self._og_directory = str(sh.pwd()).strip('\n')
        self._dest_directory = path

    def __enter__(self):
        sh.cd(self._dest_directory)

    def __exit__(self, exception_type, exception_value, traceback):
        sh.cd(self._og_directory)


def make_local_repo(book_path):

    with CdContext(book_path):

        repo = git.Repo.init('./')

        for _file in repo.untracked_files:
            filetype = os.path.splitext(_file)[1]
            if filetype not in IGNORE_FILES:
                sh.git('add', _file)

        try:
            # note the double quotes
            sh.git('commit', '-m', '"Initial import from Project Gutenberg"')
        except sh.ErrorReturnCode_1:
            print "we have already created this repo locally, aborting"


class NewFilesHandler():
    """ NewFilesHandler - templates and copies additional files to book repos

    """
    def __init__(self, book_id, book_path):
        self.meta = EbookRecord(book_id)
        self.book_path = book_path

        package_loader = jinja2.PackageLoader('gitenberg', 'templates')
        self.env = jinja2.Environment(loader=package_loader)
        self.template_readme()
        self.copy_files()

    def template_readme(self):
        template = self.env.get_template('README.rst.j2')
        readme_text = template.render(title=self.meta.title, author=self.meta.author)
        #print type(self.meta.title), self.meta.title
        #print type(self.meta.author), self.meta.author

        readme_path = "{0}/{1}".format(self.book_path, 'README.rst')
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


def make(book_id):
    book_path = path_to_library_book(book_id)
    make_local_repo(book_path)
    NewFilesHandler(book_id, book_path)
