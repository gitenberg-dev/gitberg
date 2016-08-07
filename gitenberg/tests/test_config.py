#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import yaml

from mock import MagicMock

from gitenberg.config import ConfigFile

class TestConfig(unittest.TestCase):
    def setUp(self):
        # mock reading the on-disk config file with sample yaml
        ConfigFile._read = MagicMock(return_value=example_config_yaml())
        self.cf = ConfigFile()

    def test_file_path(self):
        self.assertNotEqual(self.cf.file_path,
                            None)
        self.assertTrue(self.cf.file_path.endswith('gitberg/config.yaml'))

    def test_data(self):
        self.assertEqual(self.cf.data,
                         example_config_data())

    def test_yaml(self):
        self.assertEqual(
            load_yaml(self.cf.yaml()),
            load_yaml(example_config_yaml())
        )

def example_config_data():
    return {
        'gh_email': 'user@domain.example',
        'gh_password': 'barfoo',
        'rdf_library': 'path/to/rdf/file',
        'library_path': 'path/to/library/',
        'gh_user': 'agithubuser'
    }

def example_config_yaml():
    return '''
        gh_email: user@domain.example
        gh_password: barfoo
        gh_user: agithubuser
        library_path: path/to/library/
        rdf_library: path/to/rdf/file
    '''

def load_yaml(yaml_source):
    return yaml.load(yaml_source)
