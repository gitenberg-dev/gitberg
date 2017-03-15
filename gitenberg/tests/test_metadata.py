import os
import unittest
import yaml
import json

from gitenberg.metadata.pandata import Pandata


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/pandata.yaml')
TESTDATA_YAMLFILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/testoutput.yaml')
EDITIONTEST_FILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/editions.yaml')
TEST_YAML_STRING = '''
_repo: Metamorphosis_5200
creator:
  author:
    agent_name: Kafka, Franz
    alias: Kafka, F. (Franz)
    birthdate: 1883
    deathdate: 1924
    gutenberg_agent_id: '1735'
    url: http://www.gutenberg.org/2009/agents/1735
    wikipedia: http://en.wikipedia.org/wiki/Franz_Kafka
subjects:
- '!lcsh:Psychological fiction'
- '!lcc:PT'
- '!lcsh:Metamorphosis -- Fiction'
title: Metamorphosis
url: http://www.gutenberg.org/ebooks/5200
'''


class PandataTest(unittest.TestCase):
    def test_smart_properties(self):
        pandata = Pandata(TESTDATA_FILENAME)
        #print pandata.metadata
        self.assertEqual(pandata.publication_date,'2007-03-03')
        pandata.metadata["gutenberg_issued"] = None
        self.assertNotEqual(pandata.publication_date,'2007-03-03')
        self.assertEqual(pandata._edition,'Space-Viking')
        self.assertTrue(pandata.subjects[0][0] in ('lcsh','lcc'))

    def test_load_from_url(self):
        pandata = Pandata('https://github.com/gitenberg-dev/metadata/raw/master/samples/pandata.yaml')
        self.assertEqual(pandata._edition,'Space-Viking')
    
    def test_load_from_string(self):
        pandata = Pandata()
        pandata.load(TEST_YAML_STRING)
        self.assertEqual(pandata.authnames()[0],'Kafka, Franz')
    
        
    
    def test_editions(self):
        pandata = Pandata(EDITIONTEST_FILENAME)
        (ed1,ed2) = pandata.get_edition_list()
        self.assertEqual(ed1.publisher, "Project Gutenberg")
        self.assertEqual(ed2.publisher, "Recovering the Classics")
        self.assertEqual(ed2.isbn, "9781111122223")
        self.assertEqual(ed1.isbn, "")
        self.assertEqual(ed1.edition_identifiers['edition_id'], "repo:Space-Viking_20728#default")
        self.assertEqual(ed2.edition_identifiers['edition_id'], u'repo:Space-Viking_20728#9781111122223')
        pandata = Pandata('https://github.com/gitenberg-dev/metadata/raw/master/samples/pandata.yaml')
        [ed] = pandata.get_edition_list()

if __name__ == '__main__':
    unittest.main()