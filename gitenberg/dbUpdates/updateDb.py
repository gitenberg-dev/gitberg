import psycopg2
import yaml
import os
import six # check file types
from gitenberg import book as Book
import util

# for parsing yaml tags
def default_ctor(loader, tag_suffix, node):
    return tag_suffix + ' ' + node.value
yaml.add_multi_constructor('!lcc', default_ctor)
yaml.add_multi_constructor('!lcsh', default_ctor)


NUM_BOOK_COLS = 11 # database table constant
#conn = psycopg2.connect("dbname=stuff user=marc")
#cur = conn.cursor()

def updateDB(repo_name, sqlCur, sqlConn):
    sqlExists = "SELECT count(*) FROM Book WHERE book_id = %s"
    sqlInsertBook = "INSERT INTO book VALUES (" + \
                    "%s, "*(NUM_BOOK_COLS-1) + "%s)"
    sqlUpdate = """UPDATE book SET
        (repo_name, title, language, description, author, gutenberg_type,
         gutenberg_bookshelf, subjects, full_text, num_downloads) = (""" + \
             "%s, "*(NUM_BOOK_COLS-2) + "%s)" + \
             "WHERE book_id=%s"

    book = Book.Book(None, repo_name=repo_name)
    # clone book if needed
    if not book.local_repo:
        book.clone_from_github()
        
    # fast forward only on server, should be fine
    book.local_repo.git.remote("origin").pull() 
    with util.cd(book.local_repo.repo_path): # path to working dir of repo
        # TODO generate yaml from rdf
        if os.path.isfile("metadata.yaml"):
            with open("metadata.yaml") as f:
                data = yaml.load(f)
                sqlCur.execute(sqlExists, (data['identifiers']['gutenberg'],))
                count = sqlCur.fetchone()
                record = makeBookRecordFromRepo(repo_name, data)
                if count[0] == 1:
                    sqlCur.execute(sqlUpdate, record[1:] + [record[0]])
                elif count[0] == 0:
                    sqlCur.execute(sqlInsertBook, record)
                # TODO gather author and cover metadata
                sqlConn.commit()

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
    return values # (names, values)

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
