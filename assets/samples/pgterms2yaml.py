#!/usr/bin/python

#
#    pgterms2yaml
#
#    Copyright 2015  Gluejar, Inc. 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import xml.sax
import xml.sax.handler

from __future__ import print_function




class Handler(xml.sax.handler.ContentHandler):
    """Quick XML ContentHandler"""

    def __init__(self):

        self.path = []
        self.pathStr = ""
        self.parentPathStr = ""
        self.result = dict()

    def startDocument(self):
        print('-----')

    def endDocument(self):
        print('-----')

    
    def startElement(self, name, attrs):

        self.parentPathStr = "/" + "/".join(self.path)
        self.path.append(name)
        self.pathStr = "/" + "/".join(self.path)

        self.stats.startElement(self.pathStr, self.parentPathStr)

    
    def endElement(self, name):

        self.stats.endElement(self.pathStr)
        last = self.path.pop()

        if last != name:
            raise AssertionError("Closing and opening tags do not match.")

        self.pathStr = "/" + "/".join(self.path)
    
    def characters(self, content):
    
       
    def printResults(self):

        print("Results:")
        print("")
        print("{0}\t{1}\t{2}\t{3}".format(
                "path",
                "found total",
                "min(found in parent)",
                "max(found in parent)")
        )
        keys = self.stats.stats.keys()
        keys.sort()
        for p in keys:
            el = self.stats.stats[p]
            print("{0}\t{1}\t{2}\t{3}".format(
                    p,
                    el.times_total,
                    el.times_min,
                    el.times_max)
            )
        # Some debugging:
        #for p in keys:
        #    print(p)
        #    self.stats.stats[p].printMe()



def main(argv):

    # Create XmlReader:
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_validation, False)
    parser.setFeature(xml.sax.handler.feature_external_ges, False)
    parser.setFeature(xml.sax.handler.feature_external_pes, False)
    
    # Create an assign a handler to the parser:
    handler = Handler()
    parser.setContentHandler(handler)

    # process all arguments as filenames:
    for f in argv:
        print("Processing {0}...".format(f))
        parser.parse(f)
    
    print("")
    handler.printResults()


def usage():

    print("Usage: $ python pgterms2yaml.py FILE [FILE] [FILE] ...")



if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        usage()
        
