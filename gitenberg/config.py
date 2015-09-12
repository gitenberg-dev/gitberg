#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
"""
import os

import appdirs
import yaml


class ConfigFile(object):
    """ A wrapper for managing creating and reading a config file
    takes (optional) appname str kwarg,
    for testing creation/destruction """
    # TODO emit warning if config doesn't exist
    # TODO make subcommand for creating config file
    appname = 'gitberg'
    file_name = 'config.yaml'

    def __init__(self, appname=None):
        if appname:
            self.appname = appname
        self.dir = appdirs.user_config_dir(self.appname)
        self.exists_or_make()

    @property
    def file_path(self):
        return os.path.join(self.dir, self.file_name)

    def exists_or_make(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        if not os.path.exists(self.file_path):
            # FIXME: copy or template sample config file
            with open(self.file_path, 'a'):
                os.utime(self.file_path, None)

    def __repr__(self):
        return self.read()

    def read(self):
        with open(self.file_path) as _fp:
            return _fp.read()

    def parse(self):
        self.data = yaml.load(self.read())


def main():
    config = ConfigFile()
    # print config
    config.parse()
    print(config.data)

if __name__ == "__main__":
    main()
