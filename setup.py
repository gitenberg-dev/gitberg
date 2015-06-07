#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import unicode_literals
from setuptools import setup

from gitenberg import __version__

files = ['*']

setup(name='GITenberg',
      version=__version__,
      description="A library and command for interacting with the GITenberg books project",
      author='Seth Woodworth',
      author_email='seth@sethish.com',
      url='https://github.com/sethwoodworth/gitenberg',
      packages=['gitenberg', 'gitenberg.util'],
      # package_data={
      #     'gitenberg': ['gitenberg/*'],
      #     'gitenberg.util': ['gitenberg/util/*'],
      # },
      scripts=['gitbook'],
      # long_description="",
      # classifiers=[],
      # py_modules=['gitenberg'],
      test_suite='gitenberg.test',
      )
