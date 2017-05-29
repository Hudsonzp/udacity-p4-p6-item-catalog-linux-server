from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, Product, User

engine = create_engine('sqlite:///catalogproject.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

User2 = User(name="Taco Zach", email="tacozach@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

# Menu for UrbanBurger
category1 = Category(user_id=1, name="Urban Burger")

session.add(category1)
session.commit()

product2 = Product(user_id=1, name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                   sub_category="Entree", category=category1)

session.add(product2)
session.commit()


product1 = Product(user_id=1, name="French Fries", description="with garlic and parmesan",
                   sub_category="Appetizer", category=category1)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                   sub_category="Entree", category=category1)

session.add(product2)
session.commit()

product3 = Product(user_id=1, name="Chocolate Cake", description="fresh baked and served with ice cream",
                   sub_category="Dessert", category=category1)

session.add(product3)
session.commit()


# Menu for Super Stir Fry
category2 = Category(user_id=1, name="Super Stir Fry")

session.add(category2)
session.commit()


product1 = Product(user_id=1, name="Chicken Stir Fry", description="With your choice of noodles vegetables and sauces",
                   sub_category="Entree", category=category2)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name="Peking Duck",
                   description=" A famous duck dish from Beijing[1] that has been prepared since the imperial era. The meat is prized for its thin, crisp skin, with authentic versions of the dish serving mostly the skin and little meat, sliced in front of the diners by the cook", sub_category="Entree", category=category2)

session.add(product2)
session.commit()

product3 = Product(user_id=1, name="Spicy Tuna Roll", description="Seared rare ahi, avocado, edamame, cucumber with wasabi soy sauce ",
                   sub_category="Entree", category=category2)

session.add(product3)
session.commit()

# end of products ########################

print "added menu items!"
