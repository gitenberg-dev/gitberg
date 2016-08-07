#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from gitenberg import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.cf = config.ConfigFile()

    def test_config_file_path(self):
        self.assertNotEqual(self.cf.file_path, None)
        self.assertTrue(self.cf.file_path.endswith('gitberg/config.yaml'))

    def test_config_parse(self):
        # TODO: set fake prefix dir
        # test prefix dir
        pass

    def tearDown(self):
        # TODO destroy test folder
        pass
