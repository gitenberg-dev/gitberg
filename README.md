# Gitberg
![travis status](https://img.shields.io/travis/gitenberg-dev/gitberg.svg)
![PyPI version](https://img.shields.io/pypi/v/gitberg.svg)

[GITenberg](gitenberg.org) is a project to collectively curate ebooks on GitHub.
[Gitberg](https://github.com/gitenberg-dev/gitberg) is a command line tool to automate tasks on books.


## Usage

This project provides a `gitberg` command that does the following:

Current development is focused on making the tool usable for arbitrary changes of many repos.
This includes:

+ ! `gitberg report <bookid>` reports an issue in the appropriate GITenberg github repo
+ ! `gitberg get <bookid>` clones a GITenberg repo to your local system
+ ! `gitberg check` checks the build process setup and runs tests on the local book
+ ! `gitberg tag` increments the version number of the book and adds a git tag


Implemented, but not yet ported to be distributable:

+ `gitberg fetch <bookid>` fetches books from PG
+ `gitberg make <bookid>` makes a local git repo with extra files
+ `gitberg push <bookid>` creates a repo on github and pushes to it (one per book)

## Testing

To run project tests do:

    python setup.py test


## Packaging

This project is available as a python package
To build this python package, use `setup.py`

    python setup.py sdist
