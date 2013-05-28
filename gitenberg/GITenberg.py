#!/usr/bin/python
# -*- coding: utf-8 -*-
""" A script for moving Project Gutenberg ebooks to Github. """
import codecs
import cPickle as pickle
import json
from optparse import OptionParser
import os
from re import sub
import shutil
import subprocess
import sys

#import git
#import github3

import rdfparse2
from filetypes import IGNORE_FILES

#from secrets import GH_USER
#from secrets import GH_PASSWORD

import models

PICKLE_PATH     = u'./catalog.pickle'
ARCHIVE_ROOT    = u'/media/gitenberg'



def update_catalog(pickle_path=PICKLE_PATH):
    """ Use an imported repo to parse the Gutenberg XML index into a pickle
        This saves it to the file noted in PICKLE_PATH
    """
    mycat = rdfparse2.Gutenberg(pickle_path)
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
    """ Use a subprocess to add files to the local git repo """
    cmd = ['git', 'add', file_name]
    pipe = subprocess.Popen(cmd, cwd=folder)
    pipe.wait()


def git_commit(message, folder):
    """ Use a subprocess to add commit a git repo """
    cmd = ['git', 'commit', '-m', '"'+message+'"']
    pipe = subprocess.Popen(cmd, cwd=folder)
    pipe.wait()


def git_add_remote_origin(remote, folder):
    """ Use a subprocess to add a remote origin to a local git repo """
    cmd = ['git', 'remote', 'add', 'origin', remote]
    pipe = subprocess.Popen(cmd, cwd=folder)
    pipe.wait()


def git_push_origin_master(folder):
    """ Use a subprocess to push the master branch of a local git repo
        to the remote origin
    """
    cmd = ['git', 'push', 'origin', 'master']
    pipe = subprocess.Popen(cmd, cwd=folder)
    pipe.wait()


def make_local_repo(folder):
    """ Create a repo and add any file not in IGNORE_FILES """
    # TODO: check if there is a .git subfolder already
    print folder
    # this is the one place we use the `git` module import
    repo = git.Repo.init(folder)
    print repo
    print repo.untracked_files
    for _file in repo.untracked_files:
        print _file
        file_path = os.path.join(folder, _file)
        file_type = os.path.splitext(_file)[1]
        if file_type not in IGNORE_FILES:
            git_add(file_path, folder)
    git_commit("Creating repo from Project Gutenberg import", folder)
    return repo


def github_sanitize_string(book):
    """ Takes a string and sanitizes it for Github's url name format """
    _title = sub("[ ',]+", '-', book.title)
    title_length = 99 - len(str(book.bookid)) - 1
    if len(_title) > title_length:
        # if the title was shortened, replace the trailing _ with an ellipsis
        repo_title = "%s__%s" % (_title[:title_length], book.bookid)
    else:
        repo_title = "%s_%s" % (_title[:title_length], book.bookid)
    return repo_title


def create_github_repo(book):
    """ takes a github title, creates a repo under the GITenberg account
        using github3.py
    """
    github = github3.login(username=GH_USER, password=GH_PASSWORD)
    if hasattr(github, 'set_user_agent'):
        github.set_user_agent('Project GITenberg: http://gitenberg.github.com/')
    org = github.organization(login='GITenberg')
    print "ratelimit: " + str(org.ratelimit_remaining)
    team = org.list_teams()[0] # only one team in the github repo
    _desc = u'%s by %s\n is a Project Gutenberg book, now on Github.' % (book.title, book.author)
    repo_title = github_sanitize_string(book)

    try:
        repo = org.create_repo(repo_title,
                description=_desc, homepage=u'http://GITenberg.github.com/',
                private=False, has_issues=True, has_wiki=False,
                has_downloads=True, team_id=int(team.id))
    except github3.GitHubError as g_exception:
        for error in g_exception.errors:
            if 'message' in error \
                and u'name already exists on this account' == error['message']:
                github_repo_title = github_sanitize_string(book)
                repo = github.repository(org.name, github_repo_title)
        if not repo:
            print g_exception.errors
            raise

    print repo.html_url
    return repo


def create_metadata_json(book, folder):
    """ Create a json metadata file that describes the repo
        :book: rdfparse.Ebook instance
        :folder: root folder of a git repo/book where the json file will be added
    """
    filename = 'metadata.json'
    keys = ['lang', 'mdate', 'bookid', 'author', 'title', 'subj', 'loc',
            'pgcat', 'desc', 'toc', 'alttitle', 'friendlytitle']
    metadata = {}

    for key in keys:
        metadata[unicode(key)] = getattr(book, key)

    print os.path.join(folder, filename)
    try:
        _file = codecs.open(os.path.join(folder, filename), 'w', 'utf-8')
        json.dump(metadata, _file, indent=4, ensure_ascii=False)
        _file.close()
        return True
    except:
        print "that file isn't in our local yet"
        return False
        
def create_metadata_sql(catalog):
        session = models.get_session()
        for book in catalog:
                b = models.Book()
                b.lang = book.lang
                b.mdate = book.mdate
                b.bookid = book.bookid
                b.author = book.author
                b.title = book.title
                b.subj = unicode(book.subj)
                b.loc = unicode(book.loc)
                b.pgcat = book.pgcat
                b.desc = book.desc
                b.toc = book.toc
                b.alttitle = unicode(book.alttitle)
                b.friendlytitle = book.friendlytitle
                session.add(b)
        session.commit()


def create_readme(book, folder, template):
    """ Create a readme file with book specific information """
    filename = 'README.rst'

    # Library of Congress Codes and subjects can have multiple items
    lcc_block = u''.join(u"    | {0}\n".format(lcc) for lcc in book.loc)
    subj_block = u''.join(u"    | {0}\n".format(subject) for subject in book.subj)

    readme_meta = u""
    # begin mass appending for the superblock
    if book.title != '':
        readme_meta += ":Title: %s\n" % book.title
    if book.author != '':
        readme_meta += ":Author: %s\n" % book.author
    if book.desc != '':
        readme_meta += ":Description: %s\n" % book.desc
    if book.lang != '':
        readme_meta += ":Language: %s\n" % book.lang
    # LCC and subj gets special handling due to severe pre-processing
    if lcc_block != '':
        readme_meta += ":LCC:\n"
        readme_meta += lcc_block
    if subj_block != '':
        readme_meta += ":Subject:\n"
        readme_meta += subj_block
    if book.bookid != '':
        readme_meta += ":Book ID: %s\n" % book.bookid

    _file = codecs.open(os.path.join(folder, filename), 'w+', 'utf-8')
    bdict = {
                'title' : book.title,
                'readme_meta' : readme_meta,
                'author' : book.author,
                'bookid' : book.bookid
                }
    readme_text = template.format(**bdict)
    _file.write(readme_text)
    _file.close()
    return True


def copy_files(folder):
    """ Copy the LICENSE and CONTRIBUTING files to each folder repo """
    files = [u'./templates/LICENSE', u'./templates/CONTRIBUTING.md']
    for _file in files:
        shutil.copy(_file, folder)
    return True


def create_etext_folder(book):
    """creates a new-type folder and moves the file into it"""
    book_dir = get_new_folder_name(book)

    try:
        os.makedirs(book_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

    file = book.filename[book.filename.rindex('/')+1:]
    try:
        os.rename(ARCHIVE_ROOT+'/'+book.filename, book_dir+'/'+file)
    except OSError as exc:
        pass #this should be handled better!
    return True


def get_new_folder_name(book):
    """generates a new-type folder for books in old-type ie. etext folders"""
    middle = "/".join([digit for digit in book.bookid[:-1]])
    end = '/%s' % book.bookid
    book_dir = ARCHIVE_ROOT + '/' + middle + end
    return book_dir


def write_index(book, repo_url):
    """ append to an index file """
    # TODO: Don't be lazy, create a real csv with all of the book data
    # or better yet, since the server and the status is stateful, sqlite
    _file = open('./index.csv', 'a')
    _file.write(u"%s\t%s" % ( repo_url, book.bookid))
    _file.close()


def upload_books(start, end):
    """ Upload books from the local system to Github
        :start: int, index of the cataloglist to begin uploading from
        :end:   int, index of the cataloglist to stop uploading to
    """
    assert start < end
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))

    _file = codecs.open('./templates/README.rst', 'r', 'utf-8')
    readme_template = _file.read()
    _file.close()

    catalog = load_catalog()
    catalog.sort(key=lambda x: int(x.bookid))

    for book in catalog[start:end]:
        upload_book(book, readme_template)


def upload_book(book, readme_template):
    """ Upload a book to github, and handle special added files """
    if 'right' in book.rights:
        # if the book has a copyright other than Public domain, ignore for now
        return
    print('\n')
    folder = get_file_path(book)
    print("folder path:\t {0}".format(folder))
    create_metadata_json(book, folder)
    create_readme(book, folder, readme_template)
    copy_files(folder)
    make_local_repo(folder)
    repo = create_github_repo(book)
    git_add_remote_origin(repo.ssh_url, folder)
    git_push_origin_master(folder)
    write_index(book, repo.ssh_url)


def run_tests():
    """ Run the test suite """
    raise NotImplementedError


def delete_git_dirs(start, end):
    """ Delete the local git repos from books
        USE WITH CAUTION
    """
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))
    assert start < end
    for book in catalog[start:end]:
        delete_git(get_file_path(book))


def delete_git(folder):
    """ Delete the local .git directory of a book folder """
    raise NotImplementedError
    # find the remote git repo url
    # issue a delete on the remote
    # delete metadata.json, README.rst, CONTRIBUTING, LICENSE
    # delete the .git directory


def update_indices(start, end):
    """ """
    assert start < end
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))
    for book in catalog[start:end]:
        update_git_index(get_file_path(book))


def update_git_index(path):
    """ """
    raise NotImplementedError


def option_callback(opt_obj, opt_str, opt_val, parser):
    """ Callback function which handles some of the command-line options.

    :param opt_obj: The actual Option Object that's created when calling
        add_option on the parser. This gets sent as part of the callback.
    :param opt_str: The option string, e.g., ``-U`` or ``--update-catalog``
    :param opt_val: The value passed on the command-line.
    :param parser: The parser itself (instance of OptionParser)
    """
    def parse_range(range_string):
        range_string = range_string[1:-1].split(',')
        # This ensures someone doesn't pass [100,200,300,etc]
        return [int(v) for i, v in enumerate(range_string) if i < 2]

    if opt_str in ('-U', '--update-catalog'):
        if update_catalog():
            sys.exit(0)
        else:
            sys.stderr.write('Error occurred updating catalog.')
            sys.exit(127)
    elif opt_str in ('-t', '--tests'):
        sys.exit(run_tests())
    elif opt_str in ('-r', '--run'):
        upload_books(*parse_range(opt_val))
    elif opt_str in ('-D', '--delete-git'):
        delete_git_dirs(*parse_range(opt_val))


if __name__ == '__main__':
    opts = OptionParser(usage='%prog [options]')
    opts.add_option('-U', '--update-catalog',
            help='Update catalog.pickle and exit',
            nargs=0,
            action='callback',
            callback=option_callback,
            )
    opts.add_option('-t', '--tests',
            help='Run unittests and exit',
            nargs=0,
            action='callback',
            callback=option_callback,
            )
    opts.add_option('-r', '--run',
            help='Run books in the range [x,y]',
            nargs=1,
            action='callback',
            callback=option_callback,
            type='str',
            )
    opts.add_option('-D', '--delete-git',
            help='Delete `.git` directories in range [x,y]',
            nargs=1,
            action='callback',
            callback=option_callback,
            type='str',
            )
    opts.add_option('-u', '--update',
            help=('Checks for changes in git directories and commits them.'
                ' Range: [x,y]'),
            nargs=1,
            action='callback',
            callback=option_callback,
            type='str',
            )
    opts.parse_args()
