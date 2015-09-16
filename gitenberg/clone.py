""" Implements functionality for cloning a gitenberg repo book from GITenberg """
import logging
import os

import sh

from .book_identity import BookRepoName
from .config import ConfigFile
from .library import GitbergLibraryManager

def clone(arg_book_name, library_path=None):
    print("run clone")
    print(arg_book_name)
    book_repo_name = BookRepoName(arg_book_name)
    vat = CloneVat(book_repo_name)

    config = ConfigFile()
    config.parse()

    message = vat.clone()
    print("cloned?")
    print(message)
    logging.info(message)

class CloneBank(object):
    """ Contains 
    """
    pass


class CloneVat(object):
    """ An object for cloning GITenberg repos
    :takes: `book_repo_name` -- a BookRepoName instance eg. `BookRepoName('Frankenstein_84)`

    """
    def __init__(self, book_repo_name, config=None):
        self.book_repo_name = book_repo_name

        # create a local instance of the library manager with the provided
        # config if available
        self.l_manager = GitbergLibraryManager(config=config)

    def library_book_dir(self):
        return os.path.join(self.l_manager.library_base_path(), self.book_repo_name.repo_name)

    def path_exists(self):
        if os.path.exists(self.library_book_dir()):
            return True
        else:
            return False

    def clone(self):
        """ clones a book from GITenberg's repo into the library
        assumes you are authenticated to git clone from repo?
        """
        # FIXME: check if this works from a server install
        logging.debug("Attempting to clone {0}".format(self.book_repo_name.repo_name))


        if self.path_exists():
            return "Local clone of {0} already exists".format(
                self.book_repo_name.repo_name)

        # TODO: rewrite using github3.py's git module
        try:
            sh.git('clone', self.book_repo_name.get_clone_url_ssh(), self.library_book_dir())
            return "Cloned {0}".format(self.book_repo_name.repo_name)
        except sh.ErrorReturnCode_128:
            # TODO: clean this up
            logging.info("clone ran into an issue, likely this already exists")
