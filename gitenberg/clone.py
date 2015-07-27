""" Implements functionality for cloning a gitenberg repo book from GITenberg
"""
import logging
import os

import sh

from .book_identity import BookRepoName

def clone(arg_book_name):
    book_repo_name = BookRepoName(arg_book_name)
    vat = CloneVat(book_repo_name)
    message = vat.clone()
    logging.info(message)


class CloneVat(object):
    """ An object for cloning GITenberg repos
    :takes: a BookRepoName instance eg. `BookRepoName('Frankenstein_84)`
    """
    def __init__(self, book_repo_name):
        self.book_repo_name = book_repo_name

    def path_exists(self):
        if os.path.exists(self.target):
            return True
        else:
            return False

    def clone(self, target=None):
        """ clones a book from GITenberg's repo into an optional `target`
        assumes you are authenticated to git clone from repo?
        :takes: `target` a str path destination to clone to
        """
        # FIXME: check if this works from a server install
        logging.debug("Attempting to clone {0}".format(self.book_repo_name.repo_name))

        if not target:
            target = self.book_repo_name.repo_name

        self.target = target
        if self.path_exists():
            return "Local clone of {0} already exists".format(
                self.book_repo_name.repo_name)

        try:
            sh.git('clone', self.book_repo_name.get_clone_url_ssh(), target)
            return "Cloned {0}".format(self.book_repo_name.repo_name)
        except sh.ErrorReturnCode_128:
            # TODO: clean this up
            logging.info("clone ran into an issue, likely this already exists")
