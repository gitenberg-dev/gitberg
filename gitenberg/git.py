""" """
import logging
from os import path

import sh

from .util.catalog import CdContext

def add(path_to_repo, path_to_file, message, new_filename=None):
    repo = GitRepo(path_to_repo)
    if new_filename:
        repo.add_file(path_to_file, new_filename)
    else:
        repo.add_file(path_to_file)
    repo.commit(message)

class GitRepo(object):
    def __init__(self, path_to_repo):
        """ :takes: a path relative to the cwd with a git repo
        """
        self.path = path_to_repo

    def add_file(self, path_to_file, new_filename=None):
        """ Adds a file to repo and stages it
            :takes: a relative path to a file to add to the git repo
        """
        self.filename = path.basename(path_to_file)
        logging.debug(path_to_file)
        logging.debug(self.path)
        sh.cp(path_to_file, self.path)

        with CdContext('./{}/'.format(self.path)):
            if new_filename:
                sh.mv(self.filename, new_filename)
                sh.git('add', new_filename)
            else:
                sh.git('add', self.filename)

    def commit(self, message):
        self.message = message
        logging.info("Comitting file: {} to {} with {}".format(
            self.filename,
            self.path,
            self.message))

        with CdContext(self.path):
            sh.git('commit', '-m', message)
