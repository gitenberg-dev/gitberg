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
      packages=['gitenberg', 'gitenberg.gitenberg', 'gitenberg.metadata', 'gitenberg.tests', 'gitenberg.util'],
      include_package_data=True,
      scripts=['bin/gitberg'],
      setup_requires=[
        'sh>=1',
      ],
      install_requires=[
          'requests>=2.7',
          'uritemplate.py>=0.3.0',
          'github3.py>=1.0.0',
          'GitPython>=2.1.8',
          'docopt>=0.6',
          'sh>=1',
          'Jinja2>=2.7',
          'semver==2.2.0',
          'tox>=2.5.0',
          'appdirs==1.4.0',
          'beautifulsoup4>=4.6.0',
          'wikipedia==1.4.0',
          'six>=1.10.0',
          'pymarc==3.0.3',
          'PyYAML==3.11',
          'SPARQLWrapper==1.6.4',
          'html5lib==1.0.1',
          'isodate==0.5.1',
          'pytz>=2016.6.1',
          'pyparsing==2.1.10',
          'rdflib==4.2.0',
          'rdflib-jsonld==0.3',
          'mock==2.0.0',
          'cffi>=1.9.1',
          'cairocffi==0.8.0',
          'pycparser>=2.17',
          'cryptography>=1.7.2',
          'pyepub==0.3.2',
          'python-dateutil>=2.6.0',
          'pyasn1>=0.4.2',
          'pyOpenSSL>=0.13',
          'certifi>=2017.4.17',
          'cryptography>=2.1.4',
      ],
      test_suite='nose.collector',
      tests_require=[
          'nose',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3.4',
      ],
      keywords="books ebooks gitenberg gutenberg epub metadata",
      )
