from flask import Blueprint, request
from api.models import db
from api.core import create_response, serialize_list, logger
from sqlalchemy import inspect

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
    username = request.args.get('username')
    password = request.args.get('password')

    if not username or not password:
        return create_response(status=400)

    result = db.session.execute('INSERT INTO User (username, password) VALUES (:username, :password)', {'username': username, 'password': password})
    print(result)
    return create_response(status=200)


@main.route("/login", methods=['POST'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    result = db.session.execute('SELECT * FROM User WHERE username=:username', {'username': username})
    
    user = result.fetchone()

    if user:
        if user.password == password:
            return create_response(data={'userId': user.userId})
        else:
            return create_response(status=401)
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