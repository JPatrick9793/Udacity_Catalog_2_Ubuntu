#! --shebang
from flask import request, g, Flask, jsonify, make_response, render_template
from flask import redirect, url_for, flash
from flask.ext.httpauth import HTTPBasicAuth
from flask import session as login_session

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from Database import Base, Item, User, Category

import httplib2
import requests
import json
import random
import string

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
auth = HTTPBasicAuth()

# read OAuth client_secret and client_id from json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# FOR ADMINISTRATIVE PURPOSES ONLY
# USED TO DELETE USERS FROM USER DB
# CANNOT LINK TO HERE FROM ANY PAGE
# USE WITH CURL OR POSTMAN TO MANUALLY DELETE USER
@app.route('/catalog/users', methods=['GET', 'DELETE'])
def getUsers():
    users = session.query(User).all()
    if request.method == 'GET':
        return jsonify(users=[i.serialize for i in users])
    if request.method == 'DELETE':
        for user in users:
            session.delete(user)
            session.commit()
        return "EVERYONE DELETED"


# MAGIC
# GANDALF PAGE
@app.route('/catalog/gandalf')
def getGandalf():
    return render_template('youShallNotPass.html')


# app route for the homepage
@app.route('/')
def determineHome():
    # if there is a login session
    if login_session['user_id']:
        return redirect(url_for('getHomeLoggedIn',
                                user_id=login_session['user_id']
                                ))
    else:
        return redirect(url_for('getHome'))


# app route for homepage, if not logged in
@app.route('/catalog')
def getHome():
        return render_template(
            'homepage_loggedout.html'
            )


# app route for homepage if logged in
@app.route('/catalog/<int:user_id>')
def getHomeLoggedIn(user_id):
    users = session.query(User).all()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    categories = session.query(Category).filter_by(user_id=user_id).all()
    return render_template(
                          'homepage.html',
                          categories=categories,
                          users=users,
                          login_session=login_session,
                          )


# to create a new category
@app.route('/catalog/category/<int:user_id>/create', methods=['POST'])
def getCreateCategory(user_id):
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    # query user from db
    user = session.query(User).filter_by(id=login_session['user_id'])
    newCategory = Category(
        name=request.form['name'],
        user_id=login_session['user_id'])
    session.add(newCategory)
    session.commit()
    return redirect(url_for('getItems',
                            user_id=login_session['user_id'],
                            category_id=newCategory.id))


# change name of a category
@app.route('/catalog/<int:user_id>/<int:category_id>/edit',
           methods=['GET', 'POST'])
def getCategoryEdit(user_id, category_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    if request.method == 'POST':
        category.name = request.form['name']
        session.commit()
        return redirect(url_for('getItems',
                                user_id=user_id,
                                category_id=category_id,
                                ))
    if request.method == 'GET':
        return render_template('getCategoryEdit.html',
                               categories=categories,
                               users=users,
                               login_session=login_session,
                               items=items,
                               cat=category)


# delete category and all associated items
@app.route('/catalog/<int:user_id>/<int:category_id>/delete',
           methods=['GET', 'POST'])
def getCategoryDelete(user_id, category_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    if request.method == 'GET':
        return render_template('getCategoryDelete.html',
                               categories=categories,
                               users=users,
                               login_session=login_session,
                               items=items,
                               cat=category)
    if request.method == 'POST':
        for i in items:
            session.delete(i)
            session.commit()
        session.delete(category)
        return redirect(url_for('determineHome'))


# page showing all items in a given category
@app.route('/catalog/<int:user_id>/<int:category_id>')
def getItems(user_id, category_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    return render_template(
                          'items.html',
                          categories=categories,
                          users=users,
                          login_session=login_session,
                          items=items,
                          cat=category,
                          )


# return json of all items within category
@app.route('/catalog/<int:user_id>/<int:category_id>/json')
def getCategoryJSON(user_id, category_id):
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    return jsonify(items=[i.serialize for i in items])


# route for post request for new item form on aside bar
@app.route('/catalog/<int:user_id>/<int:category_id>/create', methods=['POST'])
def getCreateItem(user_id, category_id):
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    # else, create a new item
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    newItem = Item(name=request.form['name'],
                   description=request.form['description'],
                   user_id=login_session['user_id'],
                   category=category_id)
    session.add(newItem)
    session.commit()
    return redirect(url_for('getItemInfo',
                            user_id=user_id,
                            category_id=category_id,
                            item_id=newItem.id))


# clicking on the aside item link will bring up the info box on the right
@app.route('/catalog/<int:user_id>/<int:category_id>/<int:item_id>')
def getItemInfo(user_id, category_id, item_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    selectedItem = session.query(Item).filter_by(id=item_id).one()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    return render_template(
                          'itemInfo.html',
                          categories=categories,
                          users=users,
                          login_session=login_session,
                          items=items,
                          cat=category,
                          selectedItem=selectedItem
                          )


# clicking edit from the getItemInfo uri will redirect here
@app.route('/catalog/<int:user_id>/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def getItemEdit(user_id, category_id, item_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    selectedItem = session.query(Item).filter_by(id=item_id).one()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    if request.method == 'GET':
        return render_template(
                              'itemEdit.html',
                              categories=categories,
                              users=users,
                              login_session=login_session,
                              items=items,
                              cat=category,
                              selectedItem=selectedItem,
                              )
    if request.method == 'POST':
        if request.form['name']:
            selectedItem.name = request.form['name']
        if request.form['description']:
            selectedItem.description = request.form['description']
        session.commit()
        return redirect(url_for('getItemInfo',
                                user_id=user_id,
                                category_id=category_id,
                                item_id=item_id))


# clicking delete from the getItemInfo uri will redirect here
@app.route('/catalog/<int:user_id>/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def getItemDelete(user_id, category_id, item_id):
    users = session.query(User).all()
    items = session.query(Item).filter_by(category=category_id).all()
    category = session.query(Category).filter_by(id=category_id).one()
    categories = session.query(Category).filter_by(user_id=user_id).all()
    selectedItem = session.query(Item).filter_by(id=item_id).one()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    if request.method == 'GET':
        return render_template(
                              'itemDelete.html',
                              categories=categories,
                              users=users,
                              login_session=login_session,
                              items=items,
                              cat=category,
                              selectedItem=selectedItem,
                              )
    if request.method == 'POST':
        session.delete(selectedItem)
        session.commit()
        return redirect(url_for('getItems',
                                user_id=user_id,
                                category_id=category_id,
                                ))


# return particular item information in json format
@app.route('/catalog/<int:user_id>/<int:category_id>/<int:item_id>/json')
def getItemJSON(user_id, category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    # Login user can only access his/her own information
    if user_id != login_session['user_id']:
        return redirect(url_for('getGandalf'))
    return jsonify(item.serialize)


# app route for login
@app.route('/login')
def getLogin():
    # create a login state string and assign it to login_session[]
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    # return the login html
    return render_template('login.html', STATE=state)


# route to logout and revoke current user's access token
@app.route('/gdisconnect')
def gdisconnect():
    # Get the access token from current login session
    access_token = login_session.get('access_token')
    # if no access token
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # url build to google to revoke token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # if google responds with 200 OK:
    if result['status'] == '200':
        # delete current info for login session[]
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        return redirect(url_for('getHome'), code=200)
    # if google returns anything but 200 OK:
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# route to connect with OAuth2.0
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token, if URL arg does not match current state
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
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
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    return output


# function to retrieve a user's ID from the User table
# uses email as parameter because it is used among
# most 3rd party authentication
def getUserID(email):
    # if the email exists within the table, return the associated ID
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    # else return None
    except:
        return None


# function to create a new User
def createUser(login_session):
    newUser = User(
                   username=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture']
                   )
    # user is added to table
    session.add(newUser)
    session.commit()
    # user is queried from table and the ID is returned
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# function that queries the User table
# using the ID and returns the object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# constructor
if __name__ == '__main__':
    app.secret_key = 'something_very_secret'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
