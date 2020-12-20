#models 
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
db = SQLAlchemy() 
from sqlalchemy_serializer import SerializerMixin


#users, categories, purchases 
#one user can make many purchases 
#one purchase can only be purchased by one user 
#let's just focus on user and purchase which is a one to many relationship

#user 
class User(db.Model, SerializerMixin): 
    user_id = db.Column(db.Integer, primary_key=True) #standard primary key 
    username = db.Column(db.String(60), nullable=False, unique=True)  #unique username - cannot be blank
    password = db.Column(db.String(64), nullable=False) #password - hashed before saving to db & cannot be blank 
    purchases = db.relationship('Purchase', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
	     return '<User {}>'.format(self.username)
 

PurchaseCategory = db.Table('purchase_categories', 
    db.Column('id', db.Integer, primary_key=True), 
    db.Column('purchase_id', db.Integer, db.ForeignKey('purchases.purchase_id')), 
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id')))

class Purchase(db.Model, SerializerMixin): 
    __tablename__ = 'purchases'
    purchase_id = db.Column(db.Integer, primary_key=True)
    amount_spent = db.Column(db.Float, nullable=False)
    name_of_purchase = db.Column(db.String(400), nullable=True) 
    date_spent = db.Column(db.DateTime, nullable=False) 
    category_name = db.Column(db.String(400), nullable=False)
    category = db.relationship("Category", secondary=PurchaseCategory, backref=db.backref('purchases'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    users = db.relationship(User)
    
    def __init__(self, amount_spent, name_of_purchase, date_spent, category_name, user_id):
        self.amount_spent = amount_spent
        self.name_of_purchase = name_of_purchase 
        self.date_spent = date_spent
        self.category_name = category_name
        self.user_id = user_id

    def __repr__(self):
	        return '<Purchase {}>'.format(self.name_of_purchase)


class Category(db.Model, SerializerMixin): 
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_limit = db.Column(db.Float, nullable=False)
    category_name = db.Column(db.String(400), nullable=True) 
    category_creator = db.Column(db.String(400), nullable=False)

    def __init__(self, category_limit, category_name, category_creator):
        self.category_limit = category_limit
        self.category_name = category_name 
        self.category_creator = category_creator

    def __repr__(self):
	        return '<Category {}>'.format(self.category_name)

