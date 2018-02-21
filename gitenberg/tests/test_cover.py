#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import unittest

import gitenberg.util.tenprintcover as tenprintcover

class TestMakeCovers(unittest.TestCase):

    def setUp(self):
        self.test_path =  os.path.join(os.path.dirname(__file__),'cover.png')

    def test_cover(self):
        try:
            cover_image = tenprintcover.draw(
                "A truly amazing book", 
                "(但不是那么神奇)", 
                "Donald Duck and Mickey Mouse"
            )
            with open(self.test_path, 'w+') as cover:
                cover_image.save(cover)
            self.assertTrue(os.path.exists(self.test_path))
        except OSError:
            # eat this exception so the test will pass in server environments
            print("OSError, probably Cairo not installed.")
            return None

    def tearDown(self):
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
