#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from gitenberg import config 

class TestConfig(unittest.TestCase):
    def setUp(self):
        # TODO delete previous folder if it exists
        self.app_name = 'test_application_gitberg_delete'
        self.cf = config.ConfigFile(appname=self.app_name)

    def test_config_file_path(self):
        self.assertNotEqual(self.cf.file_path,None)

    def test_config_parse(self):
        # TODO: set fake prefix dir
        # test prefix dir
        config.data

    def tearDown(self):
        # TODO destroy test folder
        pass
