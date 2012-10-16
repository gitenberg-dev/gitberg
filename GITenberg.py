#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
import codecs
import cPickle as pickle
import json
from optparse import OptionParser
import os
from re import sub
import shutil
import subprocess
import sys

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
    # this is the one place we use the `git` module import
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
    gh = github3.login(username=GH_USER, password=GH_PASSWORD)
    org = gh.organization(login='GITenberg')
    print "ratelimit: " + str(org.ratelimit_remaining)
    team = org.list_teams()[0] # only one team in the github repo
    _desc = u'%s by %s\n is a Project Gutenberg book, now on Github.' % (book.title, book.author)
    repo_title = github_sanitize_string(book)

    try:
        repo = org.create_repo(repo_title,
                description=_desc, homepage=u'http://GITenberg.github.com/',
                private=False, has_issues=True, has_wiki=False,
                has_downloads=True, team_id=int(team.id))
    except github3.GitHubError as g:
        for error in g.errors:
            if 'message' in error and u'name already exists on this account' == error['message']:
                github_repo_title = github_sanitize_string(book)
                repo = gh.repository(org.name, github_repo_title)
        if not repo:
            print g.errors
            raise

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
    # TODO: Don't be lazy, create a real csv with all of the book data
    # or better yet, since the server and the status is stateful, sqlite
    fp = open('./index.csv', 'a')
    fp.write(u"%s\t%s" % ( repo_url, book.bookid))
    fp.close()


def do_stuff(catalog):
    count = 0
    file = codecs.open('README_template.rst', 'r', 'utf-8')
    readme_template = file.read()
    file.close()
    catalog.sort(key=lambda x: int(x.bookid))
    for book in catalog[1191:2000]:
        if 'right' in book.rights:
            pass
        else:
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


def upload_books(start, end):
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))
    assert start < end

    file = codecs.open('README_template.rst', 'r', 'utf-8')
    readme_template = file.read()
    file.close()

    catalog = load_catalog()
    catalog.sort(key=lambda x: int(x.bookid))

    for book in catalog[start:end]:
        upload_book(book, readme_template)


def upload_book(book, readme_template):
    if 'right' in book.rights:
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
    return 0


def delete_git_dirs(start, end):
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))
    assert start < end
    for book in catalog[start:end]:
        delete_git(get_file_path(book))


def delete_git(folder):
    pass


def update_indices(start, end):
    catalog = sorted(load_catalog(), key=lambda x: int(x.bookid))
    assert start < end
    for book in catalog[start:end]:
        update_git_index(get_file_path(book))


def update_git_index(path):
    pass


def option_callback(opt_obj, opt_str, opt_val, parser):
    """Callback function which handles some of the command-line options.

    :param opt_obj: The actual Option Object that's created when calling
        add_option on the parser. This gets sent as part of the callback.
    :param opt_str: The option string, e.g., ``-U`` or ``--update-catalog``
    :param opt_val: The value passed on the command-line.
    :param parser: The parser itself (instance of OptionParser)
    """
    def parse_range(r):
        r = r[1:-1].split(',')
        # This ensures someone doesn't pass [100,200,300,etc]
        return [int(v) for i, v in enumerate(r) if i < 2]

    if opt_str in ('-U', '--update-catalog'):
        if update_catalog():
            sys.exit(0)
        else:
            sys.stderr.write('Error occurred updating catalog.')
            sys.exit(127)
    elif opt_str in ('-t', '--tests'):
        sys.exit(run_tests())
    elif opt_str in ('-r', '--run'):
        upload_books(*parse_range(opt_str))
    elif opt_str in ('-D', '--delete-git'):
        delete_git_dirs(*parse_range(opt_str))


if __name__=='__main__':
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
