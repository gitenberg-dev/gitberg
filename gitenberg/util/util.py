import os
from contextlib import contextmanager
import psycopg2

# an exception safer wrapper around cd
# maybe there's a better place in the code base for this
# from stackoverflow
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def makeTables(connection, cursor, makeBook=True, makeAuthor=True, makeCover=True, makeExternalLink=True):
    if makeBook:
        cursor.execute("""create table Book (
        book_id             int CONSTRAINT bookkey PRIMARY KEY,
        repo_name           varchar(100),
        title               varchar(100),
        language            varchar(20),
        description         text,
        author              int,
        gutenberg_type      varchar(20),
        gutenberg_bookshelf varchar(200),
        subjects            text,
        full_text           text,
        num_downloads       int
        );""")
    if makeAuthor:
        cursor.execute("""create table Author (
        author_id     int CONSTRAINT authorkey PRIMARY KEY,
        name          varchar(100),
        aliases       text,
        birth         int,
        death         int,
        wikipedia_url varchar(200)
        );""")
    if makeCover:
        cursor.execute("""create table Cover (
        cover_id       int CONSTRAINT coverkey PRIMARY KEY,
        book_id        int,
        link           varchar(200),
        default_cover  boolean
        );""")
    if makeExternalLink:
        cursor.execute("""create table External_Link (
        link_id int CONSTRAINT extlinkkey PRIMARY KEY,
        book_id int,
        url     varchar(200),
        source  varchar(200)
        );""")
    connection.commit()
