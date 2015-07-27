class BookRepoName(object):
    def __init__(self, repo_name):
        """ A representation of the identity of a Gitenberg book.
        :takes: <book_repo_name> - GITenberg repo name `Frankenstein_84`
        """
        self.repo_name = repo_name
        self.clone_url_ssh_template = u"git@github.com:GITenberg/{repo_name}.git"

    def get_clone_url_ssh(self):
        return self.clone_url_ssh_template.format(repo_name=self.repo_name)
