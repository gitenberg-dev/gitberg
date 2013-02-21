from lxml.etree import parse
import cPickle

class Ebook():
    #not sure if init is needed?
    def __init__(self):#, bookid, title, author, subj, desc=None, rights=None, toc=None, alttitle=None, friendlytitle=None, contribs = None, pgcat=None, loc=None, lang=None):#, filename=None, mdate=None):
        self.bookid = u''#bookid #none til subj
        self.title = u''#title #multiple elements, so this SHOULD be an array
        self.author = u''#author #multiple elements, so this SHOULD be an array
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

    def __setitem__(self, key, element):
        if(key == 'bookid'):
            self.__dict__[key] = element[5:]
        elif(key in ['title', 'author', 'desc', 'rights', 'toc', 'friendlytitle', 'pgcat', 'lang']):
            self.__dict__[key] =  Ebook.leaf_element(element).text
        elif(key == 'subject'):
            if(Ebook.is_bag(element[0])):
                for item in element[0]:
                    self.__dict__[self.subject_split[item[0].tag]].append(Ebook.leaf_element(item).text)
            else:
                self.__dict__[self.subject_split[element[0].tag]].append(Ebook.leaf_element(element).text)
        elif(key in ['alttitle', 'contribs']): #this should also contain title and author as they can have multiple elements
            if(Ebook.is_bag(element)):
                for item in element:
                    self.__dict__[key].append(Ebook.leaf_element(item).text)
            else:
                self.__dict__[key].append(Ebook.leaf_element(element).text)
        else:
            a = 1

    def __getitem__(self, key):
        return self.__dict__[key]

    @staticmethod
    def is_bag(element):
        if(element.tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'):
            return True
        elif(len(element) != 0):
                if(element[0].tag == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag'):
                    return True
                else:
                    return False
        else:
            return False
        return False
    
    @staticmethod
    def leaf_element(element):
        leaf = element
        while(len(leaf.getchildren()) != 0):
            leaf = leaf[0]
        return leaf

    lookup_table = {
        '{http://purl.org/dc/elements/1.1/}creator': 'author',
        '{http://www.gutenberg.org/rdfterms/}friendlytitle': 'friendlytitle',
        '{http://purl.org/dc/elements/1.1/}description': 'desc',
        '{http://purl.org/dc/elements/1.1/}subject': 'subject',
        '{http://purl.org/dc/elements/1.1/}contributor': 'contribs',
        '{http://purl.org/dc/elements/1.1/}title': 'title',
        '{http://purl.org/dc/elements/1.1/}rights': 'rights',
        '{http://purl.org/dc/elements/1.1/}tableOfContents': 'toc',
        '{http://purl.org/dc/elements/1.1/}alternative': 'alttitle',
        '{http://purl.org/dc/elements/1.1/}language': 'lang',
        '{http://purl.org/dc/elements/1.1/}publisher': 'null',
        '{http://purl.org/dc/elements/1.1/}created': 'null',
        '{http://www.gutenberg.org/rdfterms/}downloads': 'null',
        '{http://purl.org/dc/elements/1.1/}type': 'pgcat'
        }

    subject_split = {
        '{http://purl.org/dc/terms/}LCC': 'loc',
        '{http://purl.org/dc/terms/}LCSH': 'subj'
        }

class Gutenberg:
    def __init__(self, pickle_path):
        self.pickle_path = pickle_path

    def parse_ebook(self, etree_book):
        new_book = Ebook()
        new_book['bookid'] = etree_book.values()[0]

        for child in etree_book.getchildren():
            new_book[new_book.lookup_table[child.tag]] = child#(new_book, child)

        return new_book

    def parse_catalog(self):
        catalog = parse('./catalog.rdf') #CHANGE THIS ON LIVE
        book_tag = '{http://www.gutenberg.org/rdfterms/}etext'
        file_tag = '{http://www.gutenberg.org/rdfterms/}file'
        books = catalog.findall(book_tag)
        files = catalog.findall(file_tag)
        book_list = []
        for book in books:
            book_list.append(self.parse_ebook(book))
        #print len(book_list)
        return book_list

    def updatecatalogue(self,):
        books = self.parse_catalog()
        pickle = open(self.pickle_path, 'wb')
        cPickle.dump(books, pickle, -1)
        pickle.close()
        return True
