from flask import Blueprint, request
from api.models import db
from api.core import create_response, serialize_list, logger
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

main = Blueprint("main", __name__)  # initialize blueprint


# function that is called when you visit /
@main.route("/")
def index():
    # you are now in the current application context with the main.route decorator
    # access the logger with the logger from api.core and uses the standard logging module
    # try using ipdb here :) you can inject yourself
    logger.info("Hello World!")
    return "Hello World!"

@main.route('/signup', methods=['POST'])
def signup():
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")
    
    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return create_response(status=400)

    try:
        result = db.session.execute('INSERT INTO User (username, password) VALUES (:username, :password)', {'username': username, 'password': password})
        db.session.commit()
    except IntegrityError:
        return create_response(status=409, message="User already exists")
    except Exception as e:
        return create_response(status=500, message="Something went wrong")
    
    # Get the userId of the user we just created so we can return it
    result = db.session.execute('SELECT userId FROM User WHERE username=:username', {'username': username})
    user = result.fetchone()

    return create_response(data={'userId': user.userId}, status=200)


@main.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")
    
    username = body.get('username')
    password = body.get('password')

    result = db.session.execute('SELECT * FROM User WHERE username=:username', {'username': username})    
    user = result.fetchone()
    result.close()

    if user:
        if user.password == password:
            return create_response(data={'userId': user.userId})
        else:
            return create_response(status=401, message="Password incorrect")
    else:
        return create_response(status=404, message="User not found")


@main.route('/friends', methods=['GET', 'POST'])
def friends():
    return Response(status=200)


@main.route('/friends/<id>', methods=['PUT', 'DELETE'])
def friend(id):
    return Response(status=200)


@main.route('/sentiments', methods=['POST'])
def sentiments():
    return Response(status=200)