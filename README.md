# Gitberg
![travis status](https://img.shields.io/travis/gitenberg-dev/gitberg.svg)
![PyPI version](https://img.shields.io/pypi/v/xgitberg.svg)

[GITenberg](gitenberg.org) is a project to collectively curate ebooks on GitHub.
[Gitberg](https://github.com/gitenberg-dev/gitberg) is a command line tool to automate tasks on books stored in git repositories.


## Usage

This project provides a `gitberg` command that does the following:

+ `gitberg fetch <bookid>` fetches books from PG
+ `gitberg make <bookid>` makes a local git repo with extra files
+ `gitberg push <bookid>` creates a repo on github and pushes to it (one per book)
+ `gitberg all <bookid> <bookend>` fetches, makes and pushes a range of books
+ `gitberg list <bookid_start>` fetches, makes and pushes a range of books

+ `gitberg apply <action> <book_repo_name>` applies an action
+ `gitberg metadata <bookid>` prints the yaml metadata


### Examples

```
gitberg list --rdf_library /Documents/gitenberg/cache/epub 181,565,576

```

### Config

Some commands require a config file before they can be used.
These commands will ask for config values to make a correct configuration.
The config file in linux is located at `~/.config/gitberg/config.yaml`.

Main config values:

    gh_user: <your github account name>
    gh_password: <your github account password>
    library_path: '~/data/library'
    rdf_library: location of your cache of the PG RDF demp
## Testing

To run project tests do:

    python setup.py test


## Packaging

This project is available as a python package. To install, use 

    pip install xgitberg
    
To build this python package, use `setup.py`

    python setup.py sdist

