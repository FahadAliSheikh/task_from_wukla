from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
#import flask_whooshalchemy as wa

app = Flask(__name__)
app.config['SECRET_KEY']="SECRETKEY"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///recipe.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# app.config['DEBUG']=True
# app.config['WHOOSH_BASE']='whoosh'
db = SQLAlchemy(app)

#Model
class Recipe(db.Model):
   # __searchable__=['name','prep_time','difficulty']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True,nullable=False)
    prep_time = db.Column(db.String(20), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    vegetarian = db.Column(db.Boolean, nullable=False)
    ratings = db.relationship('Rating', lazy=True)
   
    @validates('difficulty')
    def validate_difficulty(self, key, difficulty):
        if difficulty < 0 or difficulty >3:
            raise AssertionError('Difficulty must be between 1 and 3 ')
        return difficulty


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=True )
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'),nullable=True)
    
    @validates('value')
    def validate_value(self, key, value):
        if value < 0 or value >5:
            raise AssertionError('value must be between 1 and 5 ')
        return value
