#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import os.path
import unittest

from gitenberg import config

class TestConfig(unittest.TestCase):
    def setUp(self):
        # TODO delete previous folder if it exists
        self.app_name = 'test_application_gitberg_delete'
        self.cf = config.ConfigFile(appname=self.app_name)
        try:
            os.unlink(self.cf.file_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def test_config_file_path(self):
        self.assertNotEqual(self.cf.file_path, None)

    def test_config_parse(self):
        # TODO: set fake prefix dir
        # test prefix dir
        config.data

    def test_from_environment(self):
        os.environ['gitberg_rdf_library'] = 'test library path'
        # Verify this works even without a config file there at all.
        self.assertFalse(os.path.exists(self.cf.file_path))

        self.cf = config.ConfigFile(appname=self.app_name)
        self.assertEqual('test library path', config.data['rdf_library'])

        # Avoid leaking our test data to other tests which expect it to start as
        # empty.
        del os.environ['gitberg_rdf_library']
        config.data = {}

    def test_from_environment_uppercase(self):
        os.environ['GITBERG_RDF_LIBRARY'] = 'test library path'
        self.cf = config.ConfigFile(appname=self.app_name)
        self.assertEqual('test library path', config.data['rdf_library'])

        # Avoid leaking our test data to other tests which expect it to start as
        # empty.
        del os.environ['GITBERG_RDF_LIBRARY']
        config.data = {}

    def tearDown(self):
        # TODO destroy test folder
        pass
