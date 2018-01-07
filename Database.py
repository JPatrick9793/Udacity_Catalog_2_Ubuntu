#! --shebang
# DB FILE FOR CATALOG PROJECT
# import sys
# from sqlalchemy import Column, ForeignKey, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship
# from sqlalchemy import create_engine
from myproject import db
import random
import string
# Base = declarative_base()
secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


# create User table
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    picture = db.Column(db.String())
    email = db.Column(db.String())

    # serialize property to return information in JSON format
    @property
    def serialize(self):
        return {
               'id': self.id,
               'username': self.username,
               'email': self.email,
               }


# create category table
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    user = db.relationship(User)

    # to return JSON format
    @property
    def serialize(self):
        return {
               'name': self.name,
               'user_id': self.user_id,
               }


# create item table
class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    category = db.Column(db.Integer, ForeignKey('category.id'))
    name = db.Column(db.String(25))
    description = db.Column(db.String(75))
    user = db.relationship(User)
    categ = db.relationship(Category)

    @property
    def serialize(self):
        return {
                'id': self.id,
                'user_id': self.user_id,
                'category': self.category,
                'name': self.name,
                'description': self.description,
                }


# engine = create_engine('sqlite:///catalog.db')
# Base.metadata.create_all(engine)

db.create_all()
