#! --shebang
# DB FILE FOR CATALOG PROJECT
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import random
import string
Base = declarative_base()
secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


# create User table
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)

    # serialize property to return information in JSON format
    @property
    def serialize(self):
        return {
               'id': self.id,
               'username': self.username,
               'email': self.email,
               }


# create category table
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(15))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # to return JSON format
    @property
    def serialize(self):
        return {
               'name': self.name,
               'user_id': self.user_id,
               }


# create item table
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    category = Column(Integer, ForeignKey('category.id'))
    name = Column(String(25))
    description = Column(String(75))
    user = relationship(User)
    categ = relationship(Category)

    @property
    def serialize(self):
        return {
                'id': self.id,
                'user_id': self.user_id,
                'category': self.category,
                'name': self.name,
                'description': self.description,
                }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
