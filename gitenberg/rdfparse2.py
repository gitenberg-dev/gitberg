from lxml.etree import parse

class Ebook():
    #not sure if init is needed?
    def __init__(self):#, bookid, title, author, subj, desc=None, rights=None, toc=None, alttitle=None, friendlytitle=None, contribs = None, pgcat=None, loc=None, lang=None):#, filename=None, mdate=None):
        self.bookid = u''#bookid #none til subj
        self.title = u''#title #multiple elements
        self.author = u''#author
        self.subj = []#subj #multiple elements
        self.desc = u''#desc
        self.rights = u''#rights
        self.toc = u''#toc
        self.alttitle = []#alttitle #multiple elements
        self.friendlytitle = u''#friendlytitle
        self.contribs = []#contribs #multiple elements
        self.pgcat = u''#pgcat
        self.loc = []#loc #multiple elements
        self.lang = u''#lang
        #self.filename = filename
        #self.mdate = mdate
        
    def isBag(self, element):
        if(element.tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'):
            return True
        else:
            try:
                if(element[0].tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'):
                    return True
                else:
                    return False
            except:
                return False
        return False
        
        return False

    def set_bookID(self, element):
        self.bookid = element[5:]

    def set_title(self, element):
        #self.title.append(element.text)
        self.title = element.text #do it this way to preserve
        #print element.text
        #print element

    def set_author(self, element):
        self.author = element.text

    def set_subject(self, element):
        #check if multi-element or not
        if(self.isBag(element[0])):
            for item in element[0]:
                self.subject_split[item[0].tag](self, element[0][0])
        else:
            self.subject_split[element[0].tag](self, element[0][0])
        
    def set_loc(self, element):
        self.loc.append(element.text)

    def set_subj(self, element):
        self.subj.append(element.text)

    def set_desc(self, element):
        self.desc = element.text

    def set_rights(self, element):
        self.rights = element.text

    def set_toc(self, element):
        self.toc = element.text

    def set_alt_title(self, element):
        if(self.isBag(element)):
            for item in element:
                self.alttitle.append(item[0].text)
        self.alttitle.append(element.text)

    def set_friendlytitle(self, element):
        self.friendlytitle = element.text

    def set_contributor(self, element):
        if(self.isBag(element)):
            for item in element:
                self.contribs.append(item[0].text)
        self.contribs.append(element.text)

    def set_language(self, element):
        self.lang = element[0][0].text
        
    def set_null(self, element):
        a=1

    lookup_table = {
        '{http://purl.org/dc/elements/1.1/}creator': set_author,
        '{http://www.gutenberg.org/rdfterms/}friendlytitle': set_friendlytitle,
        '{http://purl.org/dc/elements/1.1/}description': set_desc,
        '{http://purl.org/dc/elements/1.1/}subject': set_subject,
        '{http://purl.org/dc/elements/1.1/}contributor': set_contributor,
        '{http://purl.org/dc/elements/1.1/}title': set_title,
        '{http://purl.org/dc/elements/1.1/}rights': set_rights,
        '{http://purl.org/dc/elements/1.1/}tableOfContents': set_toc,
        '{http://purl.org/dc/elements/1.1/}alternative': set_alt_title,
        '{http://purl.org/dc/elements/1.1/}language': set_language,
        '{http://purl.org/dc/elements/1.1/}publisher': set_null,
        '{http://purl.org/dc/elements/1.1/}created': set_null,
        '{http://www.gutenberg.org/rdfterms/}downloads': set_null,
        '{http://purl.org/dc/elements/1.1/}type': set_null
        }
        
    subject_split = {
        '{http://purl.org/dc/terms/}LCC': set_loc,
        '{http://purl.org/dc/terms/}LCSH': set_subj
        }

def parse_ebook(etree_book):
    new_book = Ebook()
    
    new_book.set_bookID(etree_book.values()[0])
    
    for child in etree_book.getchildren():
        # get the signiture of the element, ie 'pg:author' via child.tag
        #tag = child.tag
        # get the function out of the lookup_table that matches 'tag'
        #func = new_book.lookup_table[tag]
        # call the function on the child element
        #func(child)
        new_book.lookup_table[child.tag](new_book, child)
        
    return new_book

        # or all in one line
        #new_book.lookup_table[child.tag](element)
        
def parse_catalog():
    catalog = parse('c:\catalog.rdf') #CHANGE THIS ON LIVE
    book_tag = '{http://www.gutenberg.org/rdfterms/}etext'
    file_tag = '{http://www.gutenberg.org/rdfterms/}file'
    books = catalog.findall(book_tag)
    files = catalog.findall(file_tag)
    book_list = []
    for book in books:
        book_list.append(parse_ebook(book))
    print len(book_list)
    return book_list
