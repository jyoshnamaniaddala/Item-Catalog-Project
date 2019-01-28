from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import random
import string
from functools import wraps
from database_setup import User, States, Base, MenuItem
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').
                       read())['web']['client_id']
APPLICATION_NAME = "foods of india"
engine = create_engine('sqlite:///projectdatabase.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# creating login_session
@app.route('/login')
def showLogin():
    state = ''. join(random .choice(string .
                     ascii_uppercase + string . digits)
                     for x in xrange(32))
    login_session['state'] = state
    return render_template('loginpage.html', STATE=state)


# gconnect method
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps
                                 ("""Failed to upgrade the
                                     authorization code."""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    # specifying url
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # load json file
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    # checking with the gplus_id
    if result['user_id'] != gplus_id:
        response = make_response(json.
                                 dumps("""Token's userID doesn't match
                                       given user ID """), 401)
        response.headers['Content-Type'] = 'appliction/json'
        return response
    # checking with the client id
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.
                                 dumps("""Token's client ID
                                          does not match app's"""), 401)
        print "Token's client ID does not match app's"
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # To check whether user connected already or not
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.
                                 dumps("""Current user
                                       is already connected"""), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Storing the access token
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
    # Add new user into database
    if not user_id:
        user_id = addnewUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>welcome,'
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    flash('you are now loggined in as %s' % login_session['username'])
    return output


# To disconnect from the loggedin user
@app.route("/glogout")
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.
                                 dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # Resetting the user session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully Logged Out')
        return redirect(url_for('stateMenu'))
    else:
        # The given token was not valid.
        response = make_response(json.
                                 dumps("""Failed to revoke token
                                          for given user.""", 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# To check login whether user logged in or not
def login_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("you are not allowed to access")
            return redirect('/login')
    return decorated_function


# To show state names before login
@app.route('/')
def stateMenu():
    states = session.query(States)
    return render_template("mainpage.html", states=states)


# Showing state menu items in json file
@app.route('/state/<int:state_id>/JSON')
def stateJSON(state_id):
    state = session.query(States).filter_by(id=state_id).all()
    menuitem = session.query(MenuItem).filter_by(state_id=state_id).all()
    return jsonify(Items=[i.serialize for i in menuitem])


# Showing particular menu item in state
@app.route('/state/<int:state_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(state_id, menu_id):
    menuitem = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=menuitem.serialize)


# To show states names after login
@app.route('/states/')
@login_check
def stateMenuopen():
    states = session.query(States)
    return render_template("states.html", states=states)


# To add  the new state
@app.route('/states/new/', methods=['GET', 'POST'])
@login_check
def newState():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newState = States(name=request.form['name'],
                          user_id=login_session['user_id'])
        user_id = login_session['user_id']
        session.add(newState)
        session.commit()
        flash("news state added succesfully")
        return redirect(url_for('stateMenuopen'))
    else:
        return render_template('newstate.html')


# To Edit the state name(authenticated person only)
@app.route('/state/<int:state_id>/edit/', methods=['GET', 'POST'])
@login_check
def editState(state_id):
    editedstateItem = session.query(States).filter_by(id=state_id).one()
    owner = getUserInfo(editedstateItem.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == editedstateItem.user_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedstateItem.name = request.form['name']
                session.add(editedstateItem)
                session.commit()
                flash("state item edited")
                return redirect(url_for('stateMenuopen'))
            else:
                return render_template('editstateitem.html',
                                       state_id=state_id, item=editedstateItem)
        else:
            flash("""permission denied,this can
                     be edited by owner  %s only""" % owner.name)
            return redirect('/states/')
    else:
        return redirect('/login')


# To delete the state name(authenticated person only)
@app.route('/state/<int:state_id>/delete/', methods=['GET', 'POST'])
@login_check
def deleteState(state_id):
    deletestateItem = session.query(States).filter_by(id=state_id).one()
    owner = getUserInfo(deletestateItem.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == deletestateItem.user_id:

            if request.method == 'POST':
                session.delete(deletestateItem)
                session.commit()
                flash("state item deleted")
                return redirect(url_for('stateMenuopen'))
            else:
                return render_template('deletestateitem.html',
                                       state_id=state_id, item=deletestateItem)
        else:
            flash("""permission denied,this can be
                  deleted by owner %s only""" % owner.name)
            return redirect('/states/')
    else:
        return redirect('/login')


# To show food items of the state
@app.route('/states/<int:state_id>/')
@login_check
def stateDishes(state_id):
    state = session.query(States).filter_by(id=state_id).one()
    items = session.query(MenuItem).filter_by(state_id=state.id)
    return render_template("menu.html", state=state, items=items)


# Add new menu item(authenticated person only)
@app.route('/state/<int:state_id>/new/', methods=['GET', 'POST'])
@login_check
def newMenuItem(state_id):
    state = session.query(States).filter_by(id=state_id).one()
    owner = getUserInfo(state.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == state.user_id:
            if request.method == 'POST':
                newItem = MenuItem(name=request.form['name'],
                                   state_id=state_id,
                                   user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                flash("new item created")
                return redirect(url_for('stateDishes', state_id=state_id))
            else:
                return render_template('newmenuitem.html', state_id=state_id)
        else:
            flash("""permission denied,this can be
                  added by owner %s only""" % owner.name)
            return redirect(url_for('stateDishes', state_id=state_id))
    else:
        return redirect('/login')


# To edit menu item(authenticated person only)
@app.route('/state/<int:state_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
@login_check
def editMenuItem(state_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    owner = getUserInfo(editedItem.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == editedItem.user_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                session.add(editedItem)
                session.commit()
                flash("item edited")
                return redirect(url_for('stateDishes', state_id=state_id))
            else:
                return render_template('editmenuitem.html', state_id=state_id,
                                       menu_id=menu_id, item=editedItem)
        else:
            flash("""permission denied,this can be
                  edited by owner %s only""" % owner.name)
            return redirect('/states/')
    else:
        return redirect('/login')


# To delete menu item(authenticated person only)
@app.route('/state/<int:state_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
@login_check
def deleteMenuItem(state_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    owner = getUserInfo(itemToDelete.user_id)
    if 'username' in login_session:
        if login_session['user_id'] == itemToDelete.user_id:
            if request.method == 'POST':
                session.delete(itemToDelete)
                session.commit()
                flash("item deleted")
                return redirect(url_for('stateDishes', state_id=state_id))
            else:
                return render_template('deletemenuitem.html',
                                       state_id=state_id,
                                       menu_id=menu_id, item=itemToDelete)
        else:
            flash("""permission denied,this can be
                  deleted by owner %s only""" % owner.name)
            return redirect('/states/')
    else:
        return redirect('/login')


# To get user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# To get user information
def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None


# To add new user to database
def addnewUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
