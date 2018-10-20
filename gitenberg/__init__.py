#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from .book import Book
from .clone import clone
from .config import ConfigFile, check_config, NotConfigured
from .library import main as library
from .workflow import upload_all_books, upload_list, upload_book

__title__ = 'gitberg'
__appname__ = 'gitberg'
__version__ = '0.5.4'
__copyright__ = 'Copyright 2012-2018 Seth Woodworth and the Free Ebook Foundation'

