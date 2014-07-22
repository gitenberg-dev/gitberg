#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Makes an organized git repo of a book folder
"""

import os

import git
import jinja2
import sh

from .catalog import EbookRecord
from .filetypes import IGNORE_FILES


# TODO:
# --make repo
# --add files to repo
# initial commit
# template files into repo dir
# add those templated files on 2nd commit


def make_local_repo(book_id):
    library_path = './library'
    book_path = '{0}/{1}'.format(library_path, book_id)

    og_directory = str(sh.pwd()).strip('\n')
    # cd this way has side effects, ^ lets me go back
    sh.cd(book_path)

    #print sh.pwd()

    repo = git.Repo.init('./')
    #print repo


    #print repo.untracked_files

    for _file in repo.untracked_files:
        #print _file
        filetype = os.path.splitext(_file)[1]
        if filetype not in IGNORE_FILES:
            # I don't like my git library's add command
            sh.git('add', _file)

    try:
        # note the double quotes
        sh.git('commit', '-m', '"initial commit"')
    except sh.ErrorReturnCode_1:
        print "we have already created this repo locally, aborting"
    finally:
        # go back to the original directory we started in
        sh.cd(str(og_directory))


class TemplateLoader():
    def __init__(self, book_id):
        self.ebook_record = EbookRecord(book_id)

        self.env = jinja2.Environment(loader=jinja2.PackageLoader('gitenberg', 'templates'))



def make(book_id):
    make_local_repo(book_id)
    t = TemplateLoader(book_id)
