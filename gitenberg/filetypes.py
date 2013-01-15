#!/usr/bin/python

COMPRESSED_FILES    = ['.zip', '.rar']
IGNORE_AUDIO_FILES     = ['.mp3', '.m4b', '.ogg', '.spx', '.wav', '.raw', '.ogg~', '.mpg', '.mpeg', '.MP3', '.mp4', '.m4a', '.wma', '.aac']
AUDIO_FILES     = [u'mid', u'midi', 'sib', 'mus']
IMAGE_FILES     = ['png', 'jpg', 'GIF', u'gif', u'bmp', 'tiff', 'tif', 'jpeg', 'JPG', 'eps', 'PNG']
MASTER_FILES    = ['tei', 'rst', 'txt', 'rtf', 'tex', 'TXT']
MARKUP_FILES    = ['htm', 'html', 'xml', 'eepic', 'css', 'xp', 'svg', 'ps', 'xsl']
# Generated files
GEN_FILES       = ['pdf', 'ly', 'lit', 'prc', 'doc']
OTHER_KEEP_FILES = ['fen', 'ini']

IGNORE_FILES = IGNORE_AUDIO_FILES + COMPRESSED_FILES
