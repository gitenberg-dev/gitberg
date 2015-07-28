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

setup(name='gitberg',
      version=__version__,
      description="A library and command for interacting with the GITenberg books project",
      long_description=open('README.md').read(),
      license=open('./LICENSE').read(),
      author='Seth Woodworth',
      author_email='seth@sethish.com',
      url='https://github.com/gitenberg-dev/gitberg',
      packages=find_packages(),
      include_package_data=True,
      scripts=['gitberg'],
      install_requires=[
          'requests>=2.7',
          'uritemplate.py==0.3.0',
          'github3.py>=0.9.0',
          'docopt>=0.6',
          'sh>=1',
          'Jinja2>=2.7',
          'semver==2.2.0',
          'gitenberg.metadata==0.1.4',
      ],
      test_suite='gitenberg.test',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3.4',
      ],
      keywords="books ebooks gitenberg gutenberg epub metadata",
      zip_safe=False
      )
