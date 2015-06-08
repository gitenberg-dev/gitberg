#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import find_packages
from setuptools import setup


with open('gitenberg/__init__.py', 'r') as fd:
    reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = reg.match(line)
        if m:
            __version__ = m.group(1)
            break

setup(name='GITenberg',
      version=__version__,
      description="A library and command for interacting with the GITenberg books project",
      long_description=open('README.rst').read(),
      license=open('LICENSE').read(),
      author='Seth Woodworth',
      author_email='seth@sethish.com',
      url='https://github.com/sethwoodworth/gitenberg',
      packages=find_packages(),
      scripts=['gitberg'],
      install_requires=[
          'requests>=2.7',
          'github3.py>=0.9.9',
          'docopt>=0.6',
          'sh>=1',
          'Jinja2>=2.7',
      ],
      test_suite='gitenberg.test',
      classifiers=[
          'Development Status :: 3 - Alpha'
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
      ],
      keywords="books gutenberg metadata",
      )
