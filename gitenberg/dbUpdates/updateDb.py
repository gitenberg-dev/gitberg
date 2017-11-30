import psycopg2
import yaml
import os
import six # check file types
from gitenberg import book as Book
from gitenberg.metadata.pg_rdf import pg_rdf_to_yaml
from gitenberg.util.catalog import BookMetadata
from gitenberg.util import util

# for parsing yaml tags
def default_ctor(loader, tag_suffix, node):
    return tag_suffix + ' ' + node.value
yaml.add_multi_constructor('!lcc', default_ctor)
yaml.add_multi_constructor('!lcsh', default_ctor)


NUM_BOOK_COLS = 11 # database table constant
NUM_AUTHOR_COLS = 6
conn = psycopg2.connect("dbname=stuff user=marc")
cur = conn.cursor()

def updateDB(repo_name, sqlCur, sqlConn):
    book = Book.Book(None, repo_name=repo_name)
    # clone book if needed
    if not book.local_repo:
        book.clone_from_github()
        
    # fast forward only on server, should be fine
    book.local_repo.git.remote("origin").pull() 
    with util.cd(book.local_repo.repo_path): # path to working dir of repo
        rdfFile = "pg" + book.book_id + ".rdf"
        if os.path.isfile("metadata.yaml"):
            with open("metadata.yaml") as f:
                data = yaml.load(f)
                updateBook(sqlCur, data, repo_name)
                updateAuthor(sqlCur, data)
                # TODO gather cover metadata
                sqlConn.commit()
        elif os.path.isfile(rdfFile):
            createMetaFile(book)

def updateBook(sqlCur, data, repo_name):
    sqlExistsBook = "SELECT count(*) FROM Book WHERE book_id = %s"
    sqlInsertBook = "INSERT INTO book VALUES (" + \
                    "%s, "*(NUM_BOOK_COLS-1) + "%s)"
    sqlUpdate = """UPDATE book SET
        (repo_name, title, language, description, author, gutenberg_type,
         gutenberg_bookshelf, subjects, full_text, num_downloads) = (""" + \
             "%s, "*(NUM_BOOK_COLS-2) + "%s)" + \
             "WHERE book_id=%s"

    # update/insert book
    sqlCur.execute(sqlExistsBook, (data['identifiers']['gutenberg'],))
    count = sqlCur.fetchone()
    bookRecord = makeBookRecordFromRepo(repo_name, data)
    if count[0] == 1:
        sqlCur.execute(sqlUpdate, bookRecord[1:] + [bookRecord[0]])
    elif count[0] == 0:
        sqlCur.execute(sqlInsertBook, bookRecord)

def updateAuthor(sqlCur, data):
    sqlExistsAuthor = "SELECT count(*) FROM Author WHERE author_id = %s"
    sqlInsertAuthor = "INSERT INTO author VALUES (" + \
                      "%s, "*(NUM_AUTHOR_COLS-1) + "%s)"
    
    authorRecord = makeAuthorRecordFromRepo(data)
    sqlCur.execute(sqlExistsAuthor, (authorRecord[0],)) # 0 holds id
    count = sqlCur.fetchone()
    if count[0] == 0: # insert author
        sqlCur.execute(sqlInsertAuthor, authorRecord)
    # TODO update author

def createMetaFile(book):
    book.parse_book_metadata()
    if isinstance(book.meta, BookMetadata): #should always occur
        book.meta.enrich() # adds description
    book.save_meta() # saves as metadata.yaml
    # need permissions
    book.local_repo.add_file("metadata.yaml")
    book.local_repo.commit("created metadata")
    book.github_repo.push() # triggers call to this function with metadata existing
    
def makeBookRecordFromRepo(repo_name, yamlData):
    """names = ["book_id", "repo_name", "title", "language", "description",
             "author", "gutenberg_type", "gutenberg_bookshelf", "subjects",
             "full_text", "num_downloads"]"""
    text = None
    with open(yamlData['identifiers']['gutenberg'] + '.txt') as f:
        text = f.read()
        values = [yamlData['identifiers']['gutenberg'],
              repo_name,
              yamlData['title'],
              yamlData['language'],
              yamlData['description'],
              yamlData['creator']['author']['gutenberg_agent_id'],
              yamlData['gutenberg_type'],
              concatYamlArray(yamlData['gutenberg_bookshelf']),
              concatYamlArray(yamlData['subjects']),
              text,
              0]
    return values

def makeAuthorRecordFromRepo(yamlData):
    y = yamlData['creator']['author']
    values = [
        y['gutenberg_agent_id'],
        y['agent_name'],
        concatYamlArray(y['aliases']),
        y['birthdate'],
        y['deathdate'],
        y['wikipedia'] ]
    return values

# data: either a string or an array of strings
def concatYamlArray(data):
    if isinstance(data, six.string_types): # data is a string
        return data
    else: # data is an array of strings
        ret = ""
        for s in data:
            ret += s
            ret += ";"
        return ret
