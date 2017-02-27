""" Implements functionality for cloning a gitenberg repo book from GITenberg """
import logging
import os

import git

from . import config
from .parameters import GITHUB_ORG
from .util.catalog import get_repo_name

clone_url_ssh_template = u"git@github.com:{org_name}/{repo_name}.git"

def clone(book_repo_name, library_path=None):
    book_repo_name = get_repo_name(book_repo_name)
    logging.info("running clone for{}".format(book_repo_name))
    vat = CloneVat(book_repo_name)

    success, message = vat.clone()
    logging.info(message)
    return vat.local_repo


class CloneVat(object):
    """ An object for cloning GITenberg repos
    :takes: `book_repo_name` --  eg. `'Frankenstein_84`

    """
    def __init__(self, book_repo_name):
        self.book_repo_name = book_repo_name
        self.local_repo = None
        # create a local instance of the library manager with the provided
        # config if available

    def library_book_dir(self):
        return os.path.join(config.data['library_path'], self.book_repo_name)

    def path_exists(self):
        if os.path.exists(self.library_book_dir()):
            return True
        else:
            return False
    
    def get_clone_url_ssh(self):
        return clone_url_ssh_template.format(org_name=GITHUB_ORG, repo_name=self.book_repo_name)

    def clone(self):
        """ clones a book from GITenberg's repo into the library
        assumes you are authenticated to git clone from repo?
        returns True/False, message
        """
        logging.debug("Attempting to clone {0}".format(self.book_repo_name))

        if self.path_exists():
            return False, "Error: Local clone of {0} already exists".format(self.book_repo_name)

        try:
            self.local_repo = git.Repo.clone_from(self.get_clone_url_ssh(), self.library_book_dir())
            return True, "Success! Cloned {0}".format(self.book_repo_name)
        except git.exc.GitCommandError:
            print e
            logging.debug("clone ran into an issue, likely remote doesn't exist")
            return False, "Error git returned  a fail code"
