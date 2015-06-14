Project GITenberg
=================

Lets fork `Project Gutenberg`_ to github and call it Project GITenberg.

.. _Project Gutenberg: http://gutenberg.org


Why?
----

Project Gutenberg is awesome!
The public domain is awesome.
Git is awesome.

But Project Gutenberg doesn't use a version control system.
And they have a high barrier to entry to edit books.
Aaaand they don't have a public bug tracking system.

Moving PG to Github helps with these issues,
and has many other side-effect benefits.


Usage
-----

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


Project Gutenberg Stats
-----------------------

Estimated 1.6 million files
Reported 650 GB total
~40,000 + books

Links to:  `Home Page`_ - `Book Repositories`_ - Issues_

.. _Home Page: http://gitenberg.github.io
.. _Book Repositories: https://github.com/GITenberg/repositories
.. _Issues: https://github.com/sethwoodworth/GITenberg/issues

Testing
-------

To run project tests do:

    python setup.py test


Packaging
---------

This project is available as a python package (not yet published on PyPL).
To build this python package, use `setup.py`

    python setup.py sdist
