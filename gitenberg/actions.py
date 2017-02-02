# these methods with signature: action(repo, *args, **kwargs)
# can be applied to a repo 

from github3 import login
from github3.exceptions import UnprocessableEntity
from .book import Book


def get_id(repo):
    book = Book(None,repo_name=repo)

    repo = book.github_repo.github.repository('gutenbergbooks', repo)
    print repo.id
    return repo.id
    
def delete(repo_name):
    book = Book(None,repo_name=repo_name)

    repo = book.github_repo.github.repository('gutenbergbooks', repo_name)
    if repo:
        if repo.delete():
            print "{} deleted".format(repo_name)
        else:
            print "couldn't delete {}".format(repo_name)
    else:
        print "{} didn't exist".format(repo_name)
        
def add_metadata(repo_name):
    book = Book(None,repo_name=repo_name)
    book.parse_book_metadata()
    repo = book.github_repo.github.repository('gutenbergbooks', repo_name)
    if repo:
        try:
            result = repo.create_file('metadata.yaml', 'Add yaml metadata', book.meta.__unicode__())
            print "metadata added to {} in commit {}".format( 
                repo_name, result['commit'].as_dict()['sha']
                )
        except UnprocessableEntity:
            print "metadata.yaml already present in gutenbergbooks/{}".format(repo_name)
    else:
        print "{} didn't exist in gutenbergbooks".format(repo_name)
