#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
"""
import os

import appdirs
from six.moves import input
import yaml

from .dialog import ConfigGenerator

class NotConfigured(Exception):
    pass

# static global
data = {}

class ConfigFile(object):
    """ A wrapper for managing creating and reading a config file
    takes (optional) appname str kwarg,
    for testing creation/destruction """
    # TODO emit warning if config doesn't exist
    # TODO make subcommand for creating config file
    APP_NAME = 'gitberg'
    file_name = 'config.yaml'

    def __init__(self):
        self.app_dir = appdirs.user_config_dir(self.APP_NAME)
        self._get_or_create_config()
        self._load()

    def __repr__(self):
        return self._read()

    @property
    def file_path(self):
        return os.path.join(self.app_dir, self.file_name)

    def write(self):
        with open(self.file_path, 'wb') as self.file:
            self.file.write(self.yaml)
        return True

    def yaml(self):
        return yaml.dump(self.data,
                         default_flow_style=False)

    def _get_or_create_config(self):
        if not os.path.exists(self.app_dir):
            os.makedirs(self.app_dir)
        if not os.path.exists(self.file_path):
            # FIXME: copy or template sample config file
            with open(self.file_path, 'a'):
                os.utime(self.file_path, None)

    def _load(self):
        self.data = yaml.load(self._read())

    def _read(self):
        with open(self.file_path) as _fp:
            return _fp.read()


def check_config():
    """ Check if there is an existing config file
    if there is not, prompt to create one."""
    configfile = ConfigFile()
    try:
        configfile.data.keys()
        print("gitberg config file exists")
        print("\twould you like to edit your gitberg config file?")
    except AttributeError:
        print("No config found")
        print("\twould you like to create a gitberg config file?")

    answer = input("-->  [Y/n]")
    # By default, the answer is yes, as denoted by the capital Y
    if not answer:
        answer = 'Y'

    # If yes, generate a new configuration to be written to the config file
    if answer in 'Yy':
        print("Running gitberg config generator ...")
        config_gen = ConfigGenerator(current=data)
        config_gen.ask()
        configfile.data = config_gen.answers
        configfile.write()
        print("Config written to {}".format(configfile.file_path))
