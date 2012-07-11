#!/usr/bin/python
"""
"""
import rdfparse
from filetypes import AUDIO_FILES
from filetypes import IGNORE_FILES
from filetypes import MASTER_FILES

def update_catalog():
    pickle_path = './catalog.pickle'
    mycat = rdfparse.Gutenberg(pickle_path)
    success = mycat.updatecatalogue()
    print success

if __name__=='__main__':
    update_catalog()
