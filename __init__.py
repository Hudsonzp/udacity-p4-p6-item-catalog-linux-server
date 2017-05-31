from flask import Flask, render_template, request, redirect, jsonify, \
    url_for
from flask import flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Product, User
from flask import session as login_session
import random
import string
from functools import wraps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/FlaskApp/FlaskApp/client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog List Application"


# Connect to Database and create database session

engine = create_engine('postgresql://postgres:catalog@localhost/catalogproject.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def showLogin():
    """Login route that serves up the different OAUTH logins it helps
    to create an anti-forgery state token"""
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Connection for Google Oauth Login"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrades authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/FlaskApp/FlaskApp/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                                            connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # add provider to login session
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; \
    border-radius: 150px;-webkit-border-radius: 150px; \
    -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs endpoints

@app.route('/category/<int:category_id>/product/JSON')
def categoryListJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Product).filter_by(
        category_id=category_id).all()
    return jsonify(Products=[i.serialize for i in items])


@app.route('/category/<int:category_id>/product/<int:product_id>/JSON')
def productJSON(category_id, product_id):
    product_Item = session.query(Product).filter_by(id=product_id).one()
    return jsonify(Product_Item=product_Item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories

@app.route('/')
@app.route('/category/')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    latest_products = session.query(Product).order_by('date desc').limit(10)
    if 'username' not in login_session:
        return render_template('publiccategories.html', categories=categories,
                               latest=latest_products)
    else:
        return render_template('categories.html', categories=categories,
                               latest=latest_products)

# Create a new category


@app.route('/category/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    """allows user to created a new category. Checks if logged in"""
    if request.method == 'POST':
        newCategory = Category(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCategory)
        flash('New Category %s Successfully Created' % newCategory.name)
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


# Edit a category
@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """allows user to edit category if they created it"""
    editedCategory = session.query(
        Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit this category. Please create your own category in order to \
        edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
            flash('Category Successfully Edited %s' % editedCategory.name)
            return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category=editedCategory)


# Delete a category

@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """allows user to delete category if they created it"""
    categoryToDelete = session.query(
        Category).filter_by(id=category_id).one()
    if categoryToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete this category. Please create your own category in order to \
        delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(categoryToDelete)
        flash('%s Successfully Deleted' % categoryToDelete.name)
        session.commit()
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                               category=categoryToDelete)

# Show a product list


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/product/')
def showProduct(category_id):
    """shows a big list of products and categories"""
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Product).filter_by(
        category_id=category_id).all()
    if 'username' not in login_session:
        return render_template('publicproduct.html', categories=categories,
                               items=items, category=category, creator=creator)
    else:
        return render_template('product.html', categories=categories,
                               items=items, category=category, creator=creator)


# Create a new menu item
@app.route('/category/<int:category_id>/product/new/', methods=['GET', 'POST'])
@login_required
def newProduct(category_id):
    """allows a logged in user to make a new product. Checks form elements"""
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newItem = Product(name=request.form['name'],
                          description=request.form['description'],
                          category_id=request.form['category'],
                          user_id=category.user_id)
        session.add(newItem)
        session.commit()
        flash('New Product %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showProduct', category_id=category_id))
    else:
        return render_template('newproduct.html', category_id=category_id,
                               categories=categories)


@app.route('/category/<int:category_id>/product/<int:product_id>/')
def viewProduct(category_id, product_id):
    """view for an individual product"""
    category = session.query(Category).filter_by(id=category_id).one()
    product = session.query(Product).filter_by(id=product_id).one()
    if 'username' not in login_session:
        return render_template('viewpublicproduct.html',
                               category_id=category_id, product_id=product_id,
                               item=product)
    else:
        return render_template('viewproduct.html', category_id=category_id,
                               product_id=product_id, item=product)

# Edit a product


@app.route('/category/<int:category_id>/product/<int:product_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editProduct(category_id, product_id):
    """allows logged in user to edit a product"""
    editedItem = session.query(Product).filter_by(id=product_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).order_by(asc(Category.name))
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit this product. Please create your own product in order to \
        edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']
        # if request.form['sub_category']:
        #     editedItem.course = request.form['sub_category']
        session.add(editedItem)
        session.commit()
        flash('Product successfully edited')
        return redirect(url_for('viewProduct', category_id=category_id,
                                product_id=product_id))
    else:
        return render_template('editproduct.html', category=category,
                               categories=categories,
                               product=editedItem, category_id=category_id,
                               product_id=product_id, item=editedItem)


# Delete a menu item

@app.route('/category/<int:category_id>/product/<int:product_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteProduct(category_id, product_id):
    """allows logged in user to delete a product from the list"""
    category = session.query(Category).filter_by(id=category_id).one()
    itemToDelete = session.query(Product).filter_by(id=product_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete this product. Please create your own product in order to \
        delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showProduct', category_id=category_id))
    else:
        return render_template('deleteProduct.html', item=itemToDelete)


@app.route('/disconnect')
def disconnect():
    """logs out a user from oauth"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("you have successfull been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("your were not logged in")
        return reidrect(url_for('showCategories'))

if __name__ == "__main__":
    app.run()
