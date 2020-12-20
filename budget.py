#controller
import time 
from datetime import datetime
import os
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash, _app_ctx_stack, jsonify, json
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User, Purchase, Category
from flask_restful import reqparse, abort, Api, Resource
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import extract  
import math
from sqlalchemy import or_, and_

app = Flask(__name__) 
api = Api(app)

app.config.update(dict(
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default',

	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'budget.db')
))
app.config.from_envvar('BUDGET_SETTINGS', silent=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #here to silence deprecation warning
app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))



def format_datetime(start_datetime):
	"""Format a timestamp for display."""
	return (start_datetime).strftime('%Y-%m-%d @ %H:%M')

db.init_app(app) #initialize the database 

parser = reqparse.RequestParser()
parser.add_argument('categoryName', type=str)
parser.add_argument('categoryValue', type=float)
parser.add_argument('purchaseDate')
parser.add_argument('purchaseName', type=str)
parser.add_argument('amountSpent', type=float)


#initializes the database via the command line
@app.cli.command('initdb')
def initdb_command():
	db.create_all()
	print('Initialized the database! Good to go.')
	

#next three are helper methods 
def get_user_id(username):
	"""Convenience method to look up the id for a username."""
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None #return the user id if the user was returned in rv or else it will return in none 

@app.before_request
def before_request():
	g.user = None #create user and set it to none 
	if 'user_id' in session: #is the user logged in? 
		g.user = User.query.filter_by(user_id=session['user_id']).first()
		#pull the user who is logged in and put it in g.user 

@app.route('/')
def timeline(): 
    return redirect(url_for('homepage'))

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if g.user: #if the user is logged in.. send them to homepage
        return redirect(url_for('homepage'))
    error = None #track error 
    if request.method == 'POST': #you want to send something to the server
        user = User.query.filter_by(username=request.form['username']).first() #get their username
        if user is None: #if it doesn't match any in the database 
            error = 'Invalid username' 
        elif not check_password_hash(user.password, request.form['password']): #check their password
            error = 'Invalid password' #doesn't match 
        else: 
            flash('You were logged in')
            session['user_id']=user.user_id #log them in
            return redirect(url_for('homepage')) #send them to the home page
    return render_template('login.html', error=error) #print their error 
    
@app.route('/registration', methods=['GET', 'POST'])
def register():
	if g.user: #if user is logged in, go to their timeline 
		return redirect(url_for('homepage'))
	error = None #keep track of error 
	if request.method == 'POST':
		if not request.form['username']: #if the user didn't enter a username
			error = 'You did not enter a username, enter one to register!'
		elif not request.form['password']: #if the user didn't enter a password
			error = 'You did not enter a password, enter one to register!'
		elif get_user_id(request.form['username']) is not None: #if the username is already taken
			error = 'The username is already taken'
		else:
            #add the user, email, and hashed password into the database
			db.session.add(User(request.form['username'], generate_password_hash(request.form['password'])))
			db.session.commit() #commit to data base
			flash('Successfully registered, now log in!')
			return redirect(url_for('login')) #send them to the login page 
	return render_template('registration.html', error=error) #if everything else failed, print their error


@app.route('/logout')
def logout():
	"""Logs the user out."""
	flash('You were logged out')
	session.pop('user_id', None) #make them log out as far as the server is concerned 
	return redirect(url_for('homepage'))


@app.route('/homepage')
def homepage():
	if g.user: 
		if Category.query.filter(and_(Category.category_name== "Uncategorized", Category.category_creator==g.user.username)).first() == None: 
			print("Adding")
			new = Category(100000, "Uncategorized", g.user.username)
			#add category to the database 
			db.session.add(new) 
			db.session.commit()
		return render_template('new_purchase.html')
	else: 
		return render_template('homepage.html')
	
#	For purchases, you must implement
#	GET "/purchases" to get a list of purchases
#	POST "/purchases" to add a new purchase



class PurchaseList(Resource): 
	def get(self): 
		now = datetime.now() 
		currentMonth = now.month
		#What is was before - check if this is the idea? Only would show budget for current month but that's okay (I think?) because we don't have to worry about switching between months
		#print(Purchase.query.with_entities(Purchase.name_of_purchase, Purchase.amount_spent, Purchase.category_name).all())
		returnPurchase = Purchase.query.with_entities(Purchase.name_of_purchase, Purchase.amount_spent, Purchase.category_name).filter(and_(extract('month', Purchase.date_spent)==currentMonth, Purchase.user_id ==g.user.username)).all()
		returnPurcaseWithName = [({'name':p[0], 'amount':p[1], 'category':p[2]}) for p in returnPurchase]
		return returnPurcaseWithName

	#new purchase 
	def post(self):
		args = parser.parse_args()
		print("Printing categoryName")
		print(args['categoryName'])
		new = Purchase(args['amountSpent'],  args['purchaseName'], datetime.fromisoformat(args['purchaseDate']), args['categoryName'], g.user.username )
		#add the purchase to the database
		db.session.add(new)
		db.session.commit()
		return args, 201 #or purchases or what x


#For budget categories, you must implement
#GET "/cats" to get the list of categories
#POST "/cats" to add a new category
#DELETE "/cats/<categoryId>" to delete the category with the id <categoryId>
class CategoryList(Resource): 
	def get(self): 
		
		print("Printing Category.query.all()")
		print(Category.query.all())
		print(Category.query.with_entities(Category.category_name, Category.category_limit).filter(Category.category_creator==g.user.username))
		
		categories = Category.query.all()
		return Category.query.with_entities(Category.category_name, Category.category_limit, Category.category_name).filter(or_(Category.category_creator==g.user.username, Category.category_creator=="admin")).all()

	def post(self): 
		args = parser.parse_args()
		print("printing args in new category")
		print(args)
		print(g.user.username)
		new = Category(args['categoryValue'], args['categoryName'], g.user.username)
		#add category to the database 
		db.session.add(new) 
		db.session.commit()
		return args, 201

	def delete(self, category_name): 
		print("In here")
		args = parser.parse_args()
		print("printing args in new category")
		print(category_name)
		catToDelete = Category.query.filter(Category.category_name==category_name.strip()).first()
		print(catToDelete)
		db.session.delete(catToDelete)
		db.session.commit()
		#delete category from database
		return '', 204  

	
api.add_resource(PurchaseList, '/purchases')
api.add_resource(CategoryList, '/cats', '/cats/<category_name>')
#api.add_resource(CategoryList, '/cats/<cat_id>')
app.jinja_env.filters['datetimeformat'] = format_datetime 