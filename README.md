# Gitberg (modified for Gutenberg Books)


## Usage

This project provides a `gitberg` command that does the following:

+ `gitberg config` prompts to create a config file 
+ `gitberg metadata <bookid>` prints the yaml metadata
+ `gitberg apply add_metadata <book_repo_name>` creates a metadata.yaml file in the books repo

Other commands have not been tested.

### Examples

```
gitberg apply add_metadata 4576

```

### Config

Some commands require a config file before they can be used.
These commands will ask for config values to make a correct configuration.
The config file in linux is located at `~/.config/gitberg/config.yaml`.

Main config values:

    gh_user: <your github account name>
    gh_password: <your github account password>
    library_path: '~/data/library'
    rdf_library: location of your cache of the PG RDF dump (from https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.zip)
## Testing

To run project tests do:

    python setup.py test


## Packaging

    
To build this python package, use `setup.py`

    python setup.py sdist

