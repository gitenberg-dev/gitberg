#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
"""
import os

import appdirs
import yaml


class ConfigFile(object):
    appname = 'gitberg'
    filename = 'config.yaml'

    def __init__(self):
        self.dir = appdirs.user_config_dir(self.appname)
        self.file = os.path.join(self.dir, self.filename)
        self.exists_or_make()

    def exists_or_make(self):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        if not os.path.exists(self.file):
            # FIXME: copy or template sample config file
            with open(self.file, 'a'):
                os.utime(self.file, None)

    def __repr__(self):
        return self.read()

    def read(self):
        with open(self.file) as _fp:
            return _fp.read()

    def parse(self):
        self.data = yaml.load(self.read())


def main():
    config = ConfigFile()
    # print config
    config.parse()
    print config.data

if __name__ == "__main__":
    main()
