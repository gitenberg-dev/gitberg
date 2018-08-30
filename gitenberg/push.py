#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Syncs a local git book repo to a remote git repo (by default, github)
"""

import base64
import datetime
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import git
import github3
import requests
import semver
from travispy import TravisPy

from . import config
from .parameters import GITHUB_ORG, ORG_HOMEPAGE

logger = logging.getLogger(__name__)

class GithubRepo():

    def __init__(self, book):
        self.org_name = GITHUB_ORG
        self.org_homepage = ORG_HOMEPAGE
        self.book = book
        self._repo_token = None
        self._github_token = None
        self._travis_repo_public_key = None
        if not config.data:
            config.ConfigFile()
        self.create_api_handler()

    @property
    def repo_id(self):
        return "{}/{}".format(self.org_name, self.book.meta._repo)

    def push(self):
        self.book.local_repo.git.remote('origin').push(
            self.book.local_repo.git.refs.master, tags=True
        )

    def create_and_push(self):
        self.create_repo()
        origin = self.add_remote_origin_to_local_repo()
        origin.push(self.book.local_repo.git.refs.master)

    def update(self, message):
        self.book.local_repo.update(message)
        self.push()

    def tag(self, version, message=''):
        if version == "bump":
            old_version = self.book.meta._version
            if old_version:
                version = old_version
            else:
                version = '0.0.1'
        while version in self.book.local_repo.git.tags:
            version = semver.bump_patch(version)
        self.book.meta.metadata['_version'] =  version
        self.book.save_meta()
        self.update(message if message else 'bump version metadata')
        ref = self.book.local_repo.tag(version)
        self.push()
        logger.info("tagged and pushed " + str(ref))


    def create_api_handler(self):
        """ Creates an api handler and sets it on self """
        try:
            self.github = github3.login(username=config.data['gh_user'],
                                    password=config.data['gh_password'])
        except KeyError as e:
            raise config.NotConfigured(e)

        if hasattr(self.github, 'set_user_agent'):
            self.github.set_user_agent('{}: {}'.format(self.org_name, self.org_homepage))
        try:
            self.org = self.github.organization(self.org_name)
        except github3.GitHubError:
            logger.error("Possibly the github ratelimit has been exceeded")
            logger.info("ratelimit: " + str(self.github.ratelimit_remaining))

    def format_desc(self):
        if hasattr(self.book, 'meta'):
            title = self.book.meta.title.replace('\n', ' ')
            author = u' by {}'.format(self.book.meta.authors_short())
        else:
            title = self.book.repo_name
            author = ''
        return u'{0}{1} is a Project Gutenberg book, now on Github.'.format(title, author)

    def create_repo(self):
        try:
            self.repo = self.org.create_repository(
                self.book.repo_name,
                description=self.format_desc(),
                homepage=self.org_homepage,
                private=False,
                has_issues=True,
                has_wiki=False
            )
        except github3.GitHubError as e:
            logger.warning(u"repo already created?: {}".format(e))
            self.repo = self.github.repository(self.org_name, self.book.repo_name)

    def update_repo(self):
        try:
            self.repo = self.github.repository(self.org_name, self.book.repo_name)
            self.repo.edit(
                self.book.repo_name,
                description=self.format_desc(),
                homepage=self.org_homepage,
                private=False,
                has_issues=True,
                has_wiki=False,
                has_downloads=True
            )
        except github3.GitHubError as e:
            logger.warning(u"couldn't edit repo: {}".format(e))

    def add_remote_origin_to_local_repo(self):
        try:
            origin = self.book.local_repo.git.create_remote('origin', self.repo.ssh_url)
        except git.exc.GitCommandError:
            logger.warning("We may have already added a remote origin to this repo")
            return self.book.local_repo.git.remote('origin')
        return origin


    def github_token(self):

        if self._github_token is not None:
            return self._github_token

        token_note = "token for travis {}".format(datetime.datetime.utcnow().isoformat())
        token = github3.authorize(config.data['gh_user'], config.data['gh_password'],
                             scopes=('read:org', 'user:email', 'repo_deployment',
                                     'repo:status', 'write:repo_hook'), note=token_note)

        self._github_token = token.token
        return self._github_token

    def repo_token(self):
        if self._repo_token is not None:
            return self._repo_token
        token_note = "automatic releases for {} {}".format(
            self.repo_id,datetime.datetime.utcnow().isoformat()
        )

        token = github3.authorize(
            config.data['gh_user'],
            config.data['gh_password'],
            scopes=('public_repo'),
            note=token_note
        )
        self._repo_token = token.token
        return self._repo_token

    def public_key_for_travis_repo(self):
        if self._travis_repo_public_key is None:
            self._travis_repo_public_key =  requests.get(
                "https://api.travis-ci.org/repos/{}/key".format(self.repo_id)
            ).json().get('key', None)
        return self._travis_repo_public_key

    def travis_encrypt(self, token_to_encrypt):
        """
        return encrypted version of token_to_encrypt
        """
        # token_to_encrypt has to be string
        # if's not, assume it's unicode and enconde in utf-8

        if isinstance(token_to_encrypt, unicode):
            token_string = token_to_encrypt.encode('utf-8')
        else:
            token_string = token_to_encrypt

        repo_public_key_text = self.public_key_for_travis_repo()

        if repo_public_key_text is None:
            return None

        pubkey = repo_public_key_text.encode('utf-8')

        if 'BEGIN PUBLIC KEY' in pubkey:
            repo_public_key = serialization.load_pem_public_key(pubkey, backend=default_backend())
        elif 'BEGIN RSA PUBLIC KEY' in pubkey:
            # http://stackoverflow.com/a/32804289
            b64data = '\n'.join(pubkey.splitlines()[1:-1])
            derdata = base64.b64decode(b64data)
            repo_public_key = serialization.load_der_public_key(derdata, default_backend())
        else:
            raise Exception ('cannot parse repo public key')

        ciphertext = repo_public_key.encrypt(
            token_string,
            padding.PKCS1v15()
        )

        return base64.b64encode(ciphertext)

    def enable_travis(self):
        travis = TravisPy.github_auth(self.github_token())
        travis_repo = travis.repo(self.repo_id)
        return travis_repo.enable()


    def travis_key(self):
        if self.book.local_repo:
            travis_key = self.book.local_repo.travis_key
            if travis_key:
                return travis_key
        return self.travis_encrypt(self.repo_token())
