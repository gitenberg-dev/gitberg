#!/usr/bin/python
# -*- coding: utf-8 -*-
""" a local database backend for storing upload state and metadata """

import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///books.db')

Base = declarative_base()

class Book(Base):
    """ Metadata corresponding to a local book, and the Github instance """

    __tablename__ = 'book'

    id      = Column(u'id', Integer, primary_key=True, nullable=False)
    lang    = Column(Unicode(30))
    mdate   = Column(Unicode(30))
    bookid  = Column(Integer)
    author  = Column(Unicode(255))
    title   = Column(Unicode(255))
    subj    = Column(Unicode(255))
    loc     = Column(String(30))
    pgcat   = Column(Unicode(30))
    desc    = Column(Unicode(1024))
    toc     = Column(Unicode(5000))
    alttitle        = Column(Unicode(1024))
    friendlytitle   = Column(Unicode(1024))
    repo_url    = Column(Unicode(1024))
    web_url     = Column(Unicode(1024))
    local_path  = Column(Unicode(1024))
    status      = Column(Unicode(255)) # files created, uploaded?
    last_write  = Column(DateTime(timezone=False), default=datetime.datetime.utcnow)


def create_table():
    """ Return a sqlalchemy sqlite engine """
    return Base.metadata.create_all(engine)


def get_session():
    """ return a sqlalchemy session for the books db """
    Session = sessionmaker(bind=engine)
    return Session()

