# these methods with signature: action(repo, *args, **kwargs)
# can be applied to a repo 

from github3 import login
from github3.exceptions import UnprocessableEntity
from .book import Book
from .util import tenprintcover
from .util.catalog import get_repo_name

orgname = 'GITenberg'

def get_id(repo):
    book = Book(None,repo_name=repo)

    repo = book.github_repo.github.repository(orgname, repo)
    print repo.id
    return repo.id
    
def delete(repo_name):
    repo_name = get_repo_name(repo_name)
    book = Book(None,repo_name=repo_name)

    repo = book.github_repo.github.repository(orgname, repo_name)
    if repo:
        if repo.delete():
            print "{} deleted".format(repo_name)
        else:
            print "couldn't delete {}".format(repo_name)
    else:
        print "{} didn't exist".format(repo_name)
        
