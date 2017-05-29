import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class User(Base):
    """Used for creating a user:

    id = id for the user
    name = name of the user example: Jack Jackson
    email = email for logging in
    picture = picture from oauth login"""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """Class for categories:

    id = id for category
    name = name of the category
    user_id = the user who created the category
    user = relationship user"""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }


class Product(Base):
    """Products that belong to a category

    name = name of the product
    id = id of the product
    description = description to show on the page
    date = date it was created
    sub_category = sub category for later additions to the app
    category_id = category id it is associated with
    category = relationship parameter
    user_id = user who created it and their id
    user = relationship to user parameter"""

    __tablename__ = 'product'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    sub_category = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref=backref("products", cascade="all,delete"))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
        }

engine = create_engine('sqlite:///catalogproject.db')

Base.metadata.create_all(engine)
