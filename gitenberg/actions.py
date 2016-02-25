# these methods with signature: action(repo, *args, **kwargs)
# can be applied to a repo 

from github3 import login
from .book import Book


def get_id(repo):
    book = Book(None,repo_name=repo)

    repo = book.github_repo.github.repository('GITenberg', repo)
    print repo.id
    return repo.id