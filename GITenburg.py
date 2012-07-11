#!/usr/bin/python
"""
"""
import rdfparse
from filetypes import AUDIO_FILES
from filetypes import IGNORE_FILES
from filetypes import MASTER_FILES

def update_catalog():
    mycat = rdfparse.Gutenberg(pickle_path, self.prefs.catalog)
