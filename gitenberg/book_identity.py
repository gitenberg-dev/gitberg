#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BookRepoName(object):
    """ A representation of the identity of a Gitenberg book.
    :takes: <book_repo_name> - GITenberg repo name `Frankenstein_84`
    :provides: `class.repo_name` - local folder identifier,
                                    currently GITenberg repo name
    """
    def __init__(self, repo_name):
        # TODO: if repo_name is int make api call to translate to github url
        self.repo_name = repo_name
        self.clone_url_ssh_template = u"git@github.com:GITenberg/{repo_name}.git"


    def get_clone_url_ssh(self):
        return self.clone_url_ssh_template.format(repo_name=self.repo_name)
