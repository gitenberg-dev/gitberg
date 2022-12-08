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
with open('./LICENSE') as fd2:
    long_description = fd2.read()

setup(name='gitberg',
      version=__version__,
      description="A library and command for interacting with the GITenberg books project",
      long_description=long_description,
      long_description_content_type='text/markdown',
      license='GPLv3',
      author='Seth Woodworth',
      author_email='seth@sethish.com',
      url='https://github.com/gitenberg-dev/gitberg',
      packages=['gitenberg', 'gitenberg.gitenberg', 'gitenberg.metadata', 'gitenberg.tests', 'gitenberg.util'],
      include_package_data=True,
      scripts=['bin/gitberg'],
      setup_requires=[
        'sh>=1',
      ],
      install_requires=[
          'requests>=2.7',
          'github3.py>=3.2.0',
          'GitPython>=2.1.8',
          'docopt>=0.6',
          'sh>=1',
          'Jinja2>=2.11.3',
          'semver==2.2.0',
          'tox>=2.5.0',
          'appdirs>=1.4.0',
          'wikipedia==1.4.0',
          'six>=1.10.0',
          'pymarc>=3.0.3',
          'PyYAML>=5.4',
          'SPARQLWrapper==2.0.0',
          'pytz>=2016.6.1',
          'rdflib>6.0.1',
          'mock==2.0.0',
          'cairocffi==0.8.0',
          'python-dateutil>=2.6.0',
          'pyOpenSSL>=0.13',
      ],
      test_suite='nose.collector',
      tests_require=[
          'nose',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 3.8',
      ],
      keywords="books ebooks gitenberg gutenberg epub metadata",
      )
