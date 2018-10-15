.. :changelog:

History
-------
0.5.3 (2018-10-15)
==================
* fixed some greek repo names that were all dashes
* added "rights_note" to description
* start using missing list when iterating a range of book numbers
* suppress some debug messages


0.5.2 (2018-10-04)
==================
* added handling for an api cache to avoid running out of github calls
* save an api call by caching github repo object in book
* added modification date methods for files in git and files in rdf
* book.meta is now always a BookMetadata object
* refresh_repo action checks rdf for revised files and revises repo
* "local" keyword also turns off wikidata
* updated repo list


0.4.4 (2018-09-24)
==================
* fixed issue where gitberg refused to use the metadata from metadata.yaml, esp. repo_name
* added "local" keyword that turns off github linking in Book objects (much faster!)
* misc bugfixes
* updated requirements, esp. bs4 and html5lib

0.4.2 (2018-09-05)
==================
* fixed issue with newly fetched books and setting correct repo_name
* fixed tests which broke other tests
* parse_book_metadata moved out of command-line script into book init
* this necessitated a more uniform handling of rdf_library config

0.4.1 (2018-08-31)
==================
* no more travis. that code lives on in gitberg-build, and ebook building stuff moves to gitberg-autoupdate
* smarter commit comments

0.3.5 (2018-08-26)
==================
* packaging
* bugfixes

0.3.3 (2018-08-17)
==================
* mostly updates to add travis files
* adds code to do ebook building for releases
* adds tagging
* update to github3 API. Needed to update openssl and crypto.
* fix problematic behavior setting pubdate to today if no pubdate

0.3.1 (2017-03-29)
==================
* mostly updates to add travis files
* adds code to do ebook building for releases
* adds tagging


0.2.4 (2016-03-16)
==================
* Rewrite of config, add redf_library to config
* Adds metadata and apply actions
* includes a repo list to facilitate repo walking
* merges gitenberg.metadata package
* uses metadata package to vastly improve repo naming
* misc bugfixes
* tweak packaging to placate elastic beanstalk
* update documentation
* added example notebooks

-------
0.0.10 (2015-09-12)
==================
* Refactors and moves tests
* Adds config file crossplatform using appdirs

0.0.9 (2015-07-27)
==================
* Adds clone command

0.0.8 (2015-07-26)
==================
* Adds missing requirement

0.0.7 (2015-07-26)
==================
* Fixes `python setup.py test` when packaged

0.0.6 (2015-07-26)
==================
* Makes bugfixes and changes for packaging.
* Scaffolds out new commands via docopt

0.0.4 (2015-07-25)
==================
* Formats package for PyPi release
