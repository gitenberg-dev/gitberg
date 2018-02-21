from __future__ import print_function
import os
import unittest
import gitenberg.metadata.marc as marc
import pymarc

from gitenberg.metadata.pandata import Pandata
from gitenberg.metadata.pg_rdf import pg_rdf_to_yaml
from gitenberg.metadata.fileinfo import htm_modified_date


TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/pandata.yaml')
TESTDATA_MARCFILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/testoutput.marc.xml')
TESTDATA_PGRDFFILENAME = os.path.join(os.path.dirname(__file__), '../../assets/samples/pg20728.rdf')
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
  - !lcsh Psychological fiction
  - !lcc PT
  - !lcsh 'Metamorphosis -- Fiction'
title: Metamorphosis
url: http://www.gutenberg.org/ebooks/5200
'''

class Yaml2MarcTest(unittest.TestCase):
    def setUp(self):
        self.pandata = Pandata(TESTDATA_FILENAME)
        
    def test_pandata(self):
        print(self.pandata)
        self.assertEqual( self.pandata.gutenberg_issued , "2007-03-03")
        self.assertTrue( isinstance( self.pandata.creator , dict))
        self.assertTrue( isinstance( self.pandata.subjects[0] , tuple ))
        self.assertEqual( self.pandata.subjects[0][0] , u'lcsh' )

    def test_marc(self):
        record = marc.stub(self.pandata)
        open(TESTDATA_MARCFILENAME,"w+").write(pymarc.record_to_xml(record))
        for field in record.get_fields('650'):
            
            self.assertEqual(field.get_subfields('a')[0],  'Science fiction')
            break
        for field in record.get_fields('100'):
            self.assertEqual(field.get_subfields('a')[0],  'Piper, H. Beam')
            break
        for field in record.get_fields('700'):
            self.assertEqual(field.get_subfields('4')[0],  'ill')
            break
            
    def tearDown(self):
        if os.path.exists(TESTDATA_MARCFILENAME):
            os.remove(TESTDATA_MARCFILENAME)

class Rdf2YamlTest(unittest.TestCase):
        
    def test_conversion(self):
        yaml = pg_rdf_to_yaml(TESTDATA_PGRDFFILENAME)
        open(TESTDATA_YAMLFILENAME, "w+").write(yaml)
        pandata = Pandata(TESTDATA_YAMLFILENAME)
        self.assertEqual(pandata._edition,'book')
        self.assertTrue(pandata.subjects[0][0] in ('lcsh','lcc'))

    def tearDown(self):
        if os.path.exists(TESTDATA_YAMLFILENAME):
            os.remove(TESTDATA_YAMLFILENAME)

class FileinfoTest(unittest.TestCase):
    def test_htm_mod(self):
        self.assertEqual( htm_modified_date(TESTDATA_PGRDFFILENAME).year,2012) 

class PandataTest(unittest.TestCase):
    def test_smart_properties(self):
        pandata = Pandata(TESTDATA_FILENAME)
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