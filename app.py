from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
#import flask_whooshalchemy as wa

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRETKEY"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///recipe.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
# app.config['DEBUG']=True
# app.config['WHOOSH_BASE']='whoosh'
db = SQLAlchemy(app)

# Model


class Recipe(db.Model):
   # __searchable__=['name','prep_time','difficulty']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    prep_time = db.Column(db.String(20), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    vegetarian = db.Column(db.Boolean, nullable=False)
    ratings = db.relationship('Rating', lazy=True)

    @validates('difficulty')
    def validate_difficulty(self, key, difficulty):
        if difficulty < 0 or difficulty > 3:
            raise AssertionError('Difficulty must be between 1 and 3 ')
        return difficulty


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=True)
    recipe_id = db.Column(
        db.Integer, db.ForeignKey('recipe.id'), nullable=True)

    @validates('value')
    def validate_value(self, key, value):
        if value < 0 or value > 5:
            raise AssertionError('value must be between 1 and 5 ')
        return value


# Routes
'''
#get all recipes
this api will fetch all the recepies present in database
'''


@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    try:
        recipes = Recipe.query.all()
        output = []
        for recipe in recipes:
            recipe_data = {}
            rating_data = []
            rating_value = 0
            rating_length = 0

            recipe_data['id'] = recipe.id
            recipe_data['name'] = recipe.name
            recipe_data['prep_time'] = recipe.prep_time
            recipe_data['difficulty'] = recipe.difficulty
            recipe_data['vegetarian'] = recipe.vegetarian
            rating_length = len(recipe.ratings)
            # print(rating_length)

            # print(recipe.ratings)
            for rating in recipe.ratings:
                # print(rating.value)
                rating_data.append(rating.value)
                rating_value = rating_value+rating.value

                if rating_length:
                    average_rating = rating_value/rating_length
                recipe_data['ratings'] = rating_data
                recipe_data['average_ratings'] = average_rating

            output.append(recipe_data)
        response = jsonify({'recipes': output})
        response.status_code = 200
        return response

    except Exception as e:
        return jsonify({'error': str(e)})


'''
#create new recipte
this route will add one recepie to the database
'''


@app.route('/recipes', methods=['POST'])
def create_recipe():
    try:
        data = request.get_json()
        # print(data)
        name = data['name']
        prep_time = data['prep_time']
        difficulty = data['difficulty']
        vegetarian = data['vegetarian']
        new_recipe = Recipe(name=name, prep_time=prep_time,difficulty=difficulty, vegetarian=vegetarian)
        db.session.add(new_recipe)
        db.session.commit()
        response = jsonify({'message': 'new recipe created'})
        response.status_code = 201
        return response
    except Exception as e:
        return jsonify({'error': str(e)})


'''
#get one recipe
this route will  take id as parameter and
will return one recepie 
'''


@app.route('/recipes/<id>')
def get_one_recipe(id):
    try:
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return jsonify({'message': 'no found!'}), 404
        recipe_data = {}
        recipe_data['id'] = recipe.id
        recipe_data['name'] = recipe.name
        recipe_data['prep_time'] = recipe.prep_time
        recipe_data['difficulty'] = recipe.difficulty
        recipe_data['vegetarian'] = recipe.vegetarian
        response = jsonify({'message': recipe_data})
        response.status_code = 200
        return response
    except Exception as e:
        return jsonify({'error': str(e)})


'''
#update route
this route will take any number of parameters from schema
and will update only those values which are updated
'''


@app.route('/recipes/<id>', methods=['PUT'])
def update_recipe(id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'no data provided'}), 404
        # print(data)
        recipe = Recipe.query.filter_by(id=id).first()

        if 'name' in data:
            recipe.name = data['name']
        if 'prep_time' in data:
            recipe.prep_time = data['prep_time']
        if 'difficulty' in data:
            recipe.difficulty = data['difficulty']
        if 'vegetarian' in data:
            recipe.vegetarian = data['vegetarian']

        db.session.commit()
        return jsonify({'message': 'updated'}), 201
    except Exception as e:
        return jsonify({'error': str(e)})


'''
#delete route
this route will take id of the recipe and will delete that recipe
'''


@app.route('/recipes/<id>', methods=['DELETE'])
def delete_recipe(id):
    try:
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return jsonify({'message': 'No recipe found!'})
        db.session.delete(recipe)
        db.session.commit()
        response = jsonify({'message': 'recipe delted'})
        response.status_code = 204
        return response
    except Exception as e:
        return jsonify({'error': str(e)})


'''
#search route
this route will take recipe name as parameter and will return all the
recipes having same name
'''


@app.route('/recipes/name/<name>', methods=['POST', 'GET'])
def search_recipe(name):
    try:
        recipes = Recipe.query.filter_by(name=name).all()
        if not recipes:
            return jsonify({'message': 'No recipe found'})
        output = []
        for recipe in recipes:
            recipe_data = {}
            recipe_data['id'] = recipe.id
            recipe_data['name'] = recipe.name
            recipe_data['name'] = recipe.name
            recipe_data['prep_time'] = recipe.prep_time
            recipe_data['vegetarian'] = recipe.vegetarian
            output.append(recipe_data)
        response = jsonify({'recipes': output})
        response.status_code = 201
        return response
    except Exception as e:
        return jsonify({'error': str(e)})


# rating route
'''
this api will take recipe id as a parameter
and will add it's rating to a rating table
'''


@app.route('/recipes/<id>/rating', methods=['POST'])
def rate_recipe(id):
    try:
        recipe = Recipe.query.filter_by(id=id).first()
        if not recipe:
            return jsonify({'message': 'no recipe found'})
        data = request.get_json()
        # print(data)
        value = data['value']
        # print(value)
        new_rating = Rating(value=value, recipe_id=recipe.id)
        db.session.add(new_rating)
        db.session.commit()
        # print(new_rating)
        response = jsonify({'message': 'new recipe created'})
        response.status_code = 201
        return response
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
