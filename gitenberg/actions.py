# these methods with signature: action(repo, *args, **kwargs)
# can be applied to a repo
from __future__ import print_function

from .book import Book
from .make import NewFilesHandler
from .parameters import GITHUB_ORG as orgname

def get_id(repo, cache={}):
    book = Book(None, repo_name=repo, cache=cache)

    repo = book.github_repo.github.repository(orgname, repo)
    print(repo.id)
    return repo.id

def get_book(repo_name, cache={}):
    if isinstance(repo_name, int):
        return Book(repo_name, cache=cache)
    else:
        return Book(None, repo_name=repo_name, cache=cache)

def get_cloned_book(repo_name, cache={}):
    book = get_book(repo_name, cache=cache)
    book.clone_from_github()
    book.parse_book_metadata()
    return book

def delete(repo_name, cache={}):
    book = get_book(repo_name, cache=cache)

    repo = book.github_repo.github.repository(orgname, repo_name)
    if repo:
        if repo.delete():
            print("{} deleted".format(repo_name))
        else:
            print("couldn't delete {}".format(repo_name))
    else:
        print("{} didn't exist".format(repo_name))

def add_generated_cover(repo_name, tag=False, cache={}):
    book = get_cloned_book(repo_name, cache=cache)

    result = book.add_covers() # None if there was already a cover
    if result:
        book.local_repo.add_all_files()
        book.local_repo.commit(result)
    return book

def refresh_repo(repo_name, cache={}):
    book = get_cloned_book(repo_name, cache=cache)
    if book.meta.pg_modified() > book.source_mod_date():
        book.fetch()
    filemaker = NewFilesHandler(book)
    filemaker.copy_files()
    comment = book.add_covers()
    num_changed = book.local_repo.add_all_files()
    comment = comment + 'added {} file. '.format(num_changed) if num_changed else comment
    commit = book.local_repo.commit(comment)
    if commit or book.local_repo.no_tags():
        book.github_repo.tag('bump', message=comment)
    return book

def refresh_repo_desc(repo_name, cache={}):
    book = get_cloned_book(repo_name, cache=cache)
    book.github_repo.update_repo()
    return book
