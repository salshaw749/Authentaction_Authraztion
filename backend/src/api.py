import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/')
def test():
    return jsonify({'message':'works'})

'''
@TODO implement endpoint
    GET /drinks
'''
@app.route('/drinks' , methods=['GET'])
def drinks():

        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks':[i.short() for i in drinks]
        }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
'''
@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def drinks_detail(token):
      
    drinks = Drink.query.all()
    
    return jsonify({
        'success': True,
        'drinks':[i.long() for i in drinks]
        }), 200

'''
@TODO implement endpoint
    POST /drinks

     {
            "recipe": [
                {
                    "color": "Brown",
                    "name": "latteh",
                    "parts": 2
                }
            ],
            "title": "Latteh"
    }

'''
@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def create_drinks(token):

    data = request.get_json()

    title = data.get('title')   
    recipe = data.get('recipe')

    drink = Drink(title=title, recipe=json.dumps(recipe))
    drink.insert()



    return jsonify({
        'success': True,
        'drinks':[drink.long()]
        }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>

               
         {
            "recipe": [
                {
                    "color": "BLACK",
                    "name": "AMERCANO",
                    "parts": 1
                }
            ],
            "title": "AMERCANO"

         }
'''

    
@app.route("/drinks/<int:id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(token, id):

    data = request.get_json()


    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)


    updated_title =  data.get('title')
    updated_recipe =  data.get('recipe')

    drink.title= updated_title
    drink.recipe=json.dumps(updated_recipe)

    drink.update()
    
    return jsonify({
        'success': True, 
        'drinks': [drink.long()]
        }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>

'''

@app.route("/drinks/<int:id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(token, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(401)

    drink.delete()

    return jsonify({
            'success': True,
            'delete':id
        }), 200

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator


'''
@app.errorhandler(401)
def not_found(error):
    error_data = {
        "success": False,
        "error": 401,
        "message": "resource not found"
    }
    return jsonify(error_data), 401

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code


