#!/usr/bin/python
"""
"""
import codecs
import os
import cPickle as pickle
import json
import pprint

import git
import github3

import rdfparse
from filetypes import IGNORE_FILES

from secrets import GH_USER
from secrets import GH_PASSWORD

PICKLE_PATH     = u'./catalog.pickle'
ARCHIVE_ROOT    = u'/media/gitenberg'


def update_catalog(pickle_path=PICKLE_PATH):
    """ Use an imported repo to parse the Gutenberg XML index into a pickle 
        This saves it to the file noted in PICKLE_PATH
    """
    mycat = rdfparse.Gutenberg(pickle_path)
    success = mycat.updatecatalogue()
    print success

def load_catalog(pickle_path=PICKLE_PATH):
    """ Return catalog if local file exists, otherwise fetch it from gutenberg
    """
    if not os.path.isfile(pickle_path):
        update_catalog(pickle_path)
    return pickle.load(open(pickle_path, 'r'))

def get_file_path(book):
    """ Split a book's filename into a directory """
    # Get the path to what our DB thinks the core file is (usually a .zip)
    zip_path = os.path.join(ARCHIVE_ROOT, book.filename)
    # work backwards and get the file
    folder = os.path.split(zip_path)[0]
    return folder

def make_local_repo(folder):
    """ Create a repo and add any file not in IGNORE_FILES """
    # TODO: check if there is a .git subfolder already
    repo = git.Repo.init(folder)
    for file in repo.untracked_files:
        file_type = os.path.splitext(file)[1]
        if file_type not in IGNORE_FILES:
            repo.index.add(file)
        repo.index.commit("initial Project Gutenberg import")

def get_team(org):
    return org.list_teams()[0]

def create_github_repo(title):
    """ takes a github title, creates a repo under the GITenberg account """
    gh = github3.login(username=GH_USER, password=GH_PASSWORD)
    org = gh.organization(login='GITenberg')
    team = org.list_teams()[0] # only one team in the github repo

def create_metadata_yaml(book, folder):
    """ Create a yaml metadata file that describes the repo
        :book: rdfparse.Ebook instance
        :folder: root folder of a git repo/book where the yaml file will be added
    """
    filename = 'metadata.json'
    keys = ['lang', 'mdate', 'bookid', 'author', 'title', 'subj']
    metadata = {}

    for key in keys:
        metadata[unicode(key)] = getattr(book, key).decode("utf-8")

    print os.path.join(folder, filename)
    fp = codecs.open(os.path.join(folder, filename), 'w', 'utf-8')
    json.dump(metadata, fp, indent=4, ensure_ascii=False)
    fp.close()
    return True

if __name__=='__main__':
    #update_catalog()
    catalog = load_catalog()
    count = 0
    for book in catalog:
        print '\n'
        count += 1
        print count
        folder = get_file_path(book)
        create_metadata_yaml(book, folder)
