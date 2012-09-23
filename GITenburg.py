#!/usr/bin/python
"""
"""
import codecs
import os
import cPickle as pickle
import json
import pprint
import subprocess
import urllib
import urllib2

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

def git_add(file_name, folder):
    #git_add('exampleFile.txt', '/usr/local/example_git_repo_dir')
    cmd = ['git', 'add', file_name]
    p = subprocess.Popen(cmd, cwd=folder)
    p.wait()

def git_commit(message, folder):
    #git_commit('exampleFile.txt', '/usr/local/example_git_repo_dir')
    cmd = ['git', 'commit', '-m', '"'+message+'"']
    p = subprocess.Popen(cmd, cwd=folder)
    p.wait()

def git_add_remote_origin(remote, folder):
    #git_add_remote_origin(u'git@github.com:sethwoodworth/test.git', '/usr/local/example_git_repo_dir')
    cmd = ['git', 'remote', 'add', 'origin', remote]
    p = subprocess.Popen(cmd, cwd=folder)
    p.wait()

def git_push_origin_master(folder):
    #git_add_remote_origin(u'git@github.com:sethwoodworth/test.git', '/usr/local/example_git_repo_dir')
    cmd = ['git', 'push', 'origin', 'master']
    p = subprocess.Popen(cmd, cwd=folder)
    p.wait()

def make_local_repo(folder):
    """ Create a repo and add any file not in IGNORE_FILES """
    # TODO: check if there is a .git subfolder already
    print folder
    repo = git.Repo.init(folder)
    print repo
    print repo.untracked_files
    for file in repo.untracked_files:
        print file
        file_path = os.path.join(folder, file)
        file_type = os.path.splitext(file)[1]
        if file_type not in IGNORE_FILES:
            git_add(file_path, folder)
            #repo.index.add(file_path)
        #print repo.index
    #repo.index.commit("initial Project Gutenberg import")
    git_commit("initial Project Gutenberg import", folder)
    return repo

def create_github_repo(title):
    """ takes a github title, creates a repo under the GITenberg account """
    gh = github3.login(username=GH_USER, password=GH_PASSWORD)
    org = gh.organization(login='GITenberg')
    team = org.list_teams()[0] # only one team in the github repo
    team.create_repo( name=title, \
        description= u'A Project Gutenberg book, now on Github. \
        See [GITenberg](http=//GITenberg.github.com/) for more information',
        homepage=u'http=//GITenberg.github.com/', private=False,
        has_issues=True, has_wiki=False,\
        has_downloads=True, team_id=str(team.id))
    print "\nOrg: %s\n" % org.id
    #repo = team.create_repo(title, team_id=team.id)
    #https://api.github.com/repos/octocat/Hello-World
    url = u'https://api.github.com/orgs/GITenburg/repos'
    values = {'name': title,
        'description': u'A Project Gutenberg book, now on Github. \
        See [GITenberg](http://GITenberg.github.com/) for more information',
        'homepage': u'http://GITenberg.github.com/', 'private': False,
        'has_issues': True, 'has_wiki': False,
         'has_downloads': True, 'team_id': str(team.id)}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    res = urllib2.urlopen(req)

    return res

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
    try:
        fp = codecs.open(os.path.join(folder, filename), 'w', 'utf-8')
        json.dump(metadata, fp, indent=4, ensure_ascii=False)
        fp.close()
        return True
    except:
        print "that file isn't in our local yet"
        return False

def add_remote_origin(git_url, folder):
    """ Take a local git repo, add a remote origin to it
        :git_url: a git@github.com repo url with push privs
        :folder: root folder of the local git repo
    """


def do_stuff(catalog):
    count = 0
    for book in catalog[5:11]:
        print '\n'
        count += 1
        folder = get_file_path(book)
        print count
        print folder
        #create_metadata_yaml(book, folder)
        make_local_repo(folder)
        git_url = create_github_repo(book.title)
        git_add_remote_origin(git_url, folder)
        git_push_origin_master(folder)

if __name__=='__main__':
    #update_catalog()
    catalog = load_catalog()
    do_stuff(catalog)
