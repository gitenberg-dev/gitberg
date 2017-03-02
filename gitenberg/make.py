#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Makes an organized git repo of a book folder
"""

from __future__ import print_function
import codecs
import os
from os.path import abspath, dirname

import jinja2
import sh

from .parameters import GITHUB_ORG

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
        self.travis_files()
        self.copy_files()

    def template_readme(self):
        template = self.env.get_template('README.rst.j2')
        readme_text = template.render(
            authors=self.book.meta.authors_short(), 
            **self.book.meta.metadata
        )

        readme_path = "{0}/{1}".format(
            self.book.local_path,
            self.README_FILENAME
        )
        with codecs.open(readme_path, 'w', 'utf-8') as readme_file:
            readme_file.write(readme_text)

    def travis_files(self):
        template = self.env.get_template('.travis.yml')
        travis_text = template.render({
            'epub_title': 'book',
            'encrypted_key': self.book.github_repo.travis_key(),
            'repo_name': self.book.meta._repo,
            'repo_owner': GITHUB_ORG
        })

        fpath = os.path.join(self.book.local_path, ".travis.yml")
        with open(fpath, 'w') as f:
            f.write(travis_text)
        fpath = os.path.join(self.book.local_path, ".travis.deploy.api_key.txt")
        with open(fpath, 'w') as f:
            f.write(self.book.github_repo.travis_key())

    def copy_files(self):
        """ Copy the LICENSE and CONTRIBUTING files to each folder repo 
        Generate covers if needed. Dump the metadata.
        """
        files = [u'LICENSE', u'CONTRIBUTING.rst']
        this_dir = dirname(abspath(__file__))
        for _file in files:
            sh.cp(
                '{0}/templates/{1}'.format(this_dir, _file),
                '{0}/'.format(self.book.local_path)
            )

        # copy metadata rdf file
        sh.cp(
            self.book.meta.rdf_path,
            '{0}/'.format(self.book.local_path)
        )
        self.book.add_covers()
        self.book.meta.dump_file(os.path.join(self.book.local_path, 'metadata.yaml'))
        
