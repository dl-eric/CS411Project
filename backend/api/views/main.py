from flask import Blueprint, request, Response
from api.models import db, Person, Email
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
    return Response(status=200)

@main.route("/login", methods=['POST'])
def login():
    return Response(status=200)


@main.route('/friends', methods=['GET', 'POST'])
def friends():
    return Response(status=200)

@main.route('/friends/<id>', methods=['PUT', 'DELETE'])
def friend(id):
    return Response(status=200)

@main.route('/sentiments', methods=['POST'])
    return Response(status=200)