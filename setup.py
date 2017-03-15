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
      description="code needed for building GITenberg books",
      long_description=open('README.md').read(),
      license=open('./LICENSE').read(),
      author='Eric Hellman',
      author_email='eric@hellman.com',
      url='https://github.com/gitenberg-dev/gitberg',
      packages=['gitenberg', 'gitenberg.metadata', 'gitenberg.tests', 
        'gitenberg.travis', 'gitenberg.util'],
      include_package_data=True,
      install_requires=[
          'requests>=2.7',
          'Jinja2>=2.7',
          'PyYAML>=3.11',
      ],

      test_suite='nose.collector',
      tests_require=['nose'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3.4',
      ],
      keywords="books ebooks gitenberg gutenberg epub metadata",
      )
