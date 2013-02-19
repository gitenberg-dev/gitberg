from lxml.etree import parse

class Ebook():
    #not sure if init is needed?
    def __init__(self, bookid, title, author, subj, desc=None, rights=None, toc=None, alttitle=None, friendlytitle=None, contribs = None, pgcat=None, loc=None, lang=None, filename=None, mdate=None):
        self.bookid = bookid
        self.title = title
        self.author = author
        self.subj = subj
        self.desc = desc
        self.rights = rights
        self.toc = toc
        self.alttitle = alttitle
        self.friendlytitle = friendlytitle
        self.contribs = contribs
        self.pgcat = pgcat
        self.loc = loc
        self.lang = lang
        self.filename = filename
        self.mdate = mdate

    def set_bookID(self, element):
        self.bookid = element.text[5:]

    def set_author(self, element):
        self.author = element.text

    lookup_table = {
        '{http://purl.org/dc/elements/1.1/}creator': self.set_author,
        '{http://www.gutenberg.org/rdfterms/}friendlytitle': self.set_friendlytitle,
        '{http://purl.org/dc/elements/1.1/}description': self.set_desc,
        '{http://purl.org/dc/elements/1.1/}subject': self.set_subject,
        '{http://purl.org/dc/elements/1.1/}contributor': self.set_contributor,
        '{http://purl.org/dc/elements/1.1/}title': self.set_title,
        '{http://purl.org/dc/elements/1.1/}rights': self.set_rights,
        '{http://purl.org/dc/elements/1.1/}tableOfContents': self.set_toc,
        '{http://purl.org/dc/elements/1.1/}alternative': self.set_alt_titles,
        '{http://purl.org/dc/elements/1.1/}language': self.set_language
        }

def parse_ebook(etree_book):
    new_book = Ebook()
    
    new_book.set_bookID(etree_book.values()[0])
    
    for child in etree_book.getchildren():
        # get the signiture of the element, ie 'pg:author' via child.tag
        tag = child.tag
        # get the function out of the lookup_table that matches 'tag'
        func = new_book.lookup_table[tag]
        # call the function on the child element
        func(child)

        # or all in one line
        new_book.lookup_table[child.tag](element)
        
def parse_catalog():
    catalog = parse('c:\catalog.rdf') #CHANGE THIS ON LIVE
    book_tag = '{http://www.gutenberg.org/rdfterms/}etext'
    file_tag = '{http://www.gutenberg.org/rdfterms/}file'
    books = catalog.findall(book_tag)
    files = catalog.findall(file_tag)
    for book in books:
        parse_ebook(book)
