#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from gitenberg.config import ConfigFile

class TestConfig(unittest.TestCase):
    def setUp(self):
        # TODO delete previous folder if it exists
        self.app_name = 'test_application_gitberg_delete'
        self.cf = ConfigFile(appname=self.app_name)
        self.cf.parse()

    def test_config_file_path(self):
        self.assertEqual(
            self.cf.file_path,
            os.path.expanduser(
                '~/.config/{}/config.yaml'.format(
                    self.app_name
                )
            )
        )

    def test_config_parse(self):
        # TODO: set fake prefix dir
        # test prefix dir
        self.cf.data

    def tearDown(self):
        # TODO destroy test folder
        pass
