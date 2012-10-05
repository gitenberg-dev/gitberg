#!/usr/bin/python
"""
"""
import codecs
import os
import cPickle as pickle
import json
import shutil
import subprocess

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
    git_commit("Creating repo from Project Gutenberg import", folder)
    return repo

def create_github_repo(book):
    """ takes a github title, creates a repo under the GITenberg account
        using github3.py
    """
    gh = github3.login(username=GH_USER, password=GH_PASSWORD)
    org = gh.organization(login='GITenberg')
    team = org.list_teams()[0] # only one team in the github repo
    _desc = u'%s by %s\n is a Project Gutenberg book, now on Github.' % (book.title, book.author)
    repo_title = "%s_%s" % (book.title.decode('utf-8'), book.bookid)

    try:
        repo = org.create_repo(repo_title, description=_desc, homepage=u'http://GITenberg.github.com/', private=False, has_issues=True, has_wiki=False, has_downloads=True, team_id=int(team.id))
    except github3.GitHubError as g:
        print g.errors
        pass

    print repo.html_url
    return repo

def create_metadata_json(book, folder):
    """ Create a json metadata file that describes the repo
        :book: rdfparse.Ebook instance
        :folder: root folder of a git repo/book where the json file will be added
    """
    filename = 'metadata.json'
    keys = ['lang', 'mdate', 'bookid', 'author', 'title', 'subj', 'loc']
    metadata = {}

    for key in keys:
        metadata[unicode(key)] = getattr(book, key)#.decode("utf-8")

    print os.path.join(folder, filename)
    try:
        fp = codecs.open(os.path.join(folder, filename), 'w', 'utf-8')
        json.dump(metadata, fp, indent=4, ensure_ascii=False)
        fp.close()
        return True
    except:
        print "that file isn't in our local yet"
        return False

def create_readme(book, folder, template):
    """ Create a readme file with book specific information """
    filename = 'README.rst'
    #now for kudgy subject preprocessing
    s = u""
    s = ''.join(u"    | {0}\n".format(s) for s in book.subj)
    fp = codecs.open(os.path.join(folder, filename), 'w+', 'utf-8')
    bdict = {
                'lang' : book.lang,#.decode('utf-8'),
                'subj' : s,#.decode('utf-8'),
                'loc' : book.loc,#.decode('utf-8'),
                'title' : book.title,#.decode('utf-8'),
                'author' : book.author,#.decode('utf-8'),
                'bookid' : book.bookid#.decode('utf-8')
                }
    readme_text = template.format(**bdict)
    fp.write(readme_text)
    fp.close()
    return True

def copy_files(folder):
    """ Copy the LICENSE and CONTRIBUTING files to each folder repo """
    files = [u'./LICENSE', u'./CONTRIBUTING.md']
    for file in files:
        shutil.copy(file, folder)
    return True

def write_index(book, repo_url):
    """ append to an index file """
    fp = open('./index.csv', 'a')
    fp.write(u"%s\t%s" % ( repo_url, book.bookid))
    fp.close()


def do_stuff(catalog):
    count = 0
    file = codecs.open('README_template.rst', 'r', 'utf-8')
    readme_template = file.read()
    file.close()
    for book in catalog[15006:15200]:
        print '\n'
        count += 1
        folder = get_file_path(book)
        print "loop count:\t %s" % count
        print "folder path:\t%s" % folder
        create_metadata_json(book, folder)
        create_readme(book, folder, readme_template)
        copy_files(folder)
        make_local_repo(folder)
        repo = create_github_repo(book)
        git_add_remote_origin(repo.ssh_url, folder)
        git_push_origin_master(folder)
        write_index(book, repo.ssh_url)

if __name__=='__main__':
    #update_catalog()
    catalog = load_catalog()
    do_stuff(catalog)
