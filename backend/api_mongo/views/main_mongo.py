from flask import Blueprint, request, jsonify
from api_mongo.models import db, Person, Message
from api_mongo.core import create_response, serialize_list, logger

main_mongo = Blueprint("main_mongo", __name__)  # initialize blueprint


@main_mongo.route("/test", methods=["GET"])
def test():
    return create_response(data={"items": ["hello", "world"]})


@main_mongo.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.objects()
    return create_response(data={"messages": messages})


@main_mongo.route("/messages", methods=["POST"])
def create_message():
    data = request.json
    logger.info("Data recieved: %s", data)

    new_message = Message(
        sender=data["sender"],
        timestamp=data["timestamp"],
        content=data["content"],
        message_type=data["message_type"],
        file_id=data["file_id"],
        user_id=data["user_id"],
        friend_id=data["friend_id"],
        reactions=data["reactions"],
    )
    new_message.save()
    return create_response(message=f"Successfully created new message")


# function that is called when you visit /persons
@main_mongo.route("/persons", methods=["GET"])
def get_persons():
    persons = Person.objects()
    return create_response(data={"persons": persons})


# POST request for /persons
@main_mongo.route("/persons", methods=["POST"])
def create_person():
    data = request.json

    logger.info("Data recieved: %s", data)
    # logger.info(data.to_dict())
    if "name" not in data:
        msg = "No name provided for person."
        logger.info(msg)
        return create_response(status=422, message=msg)
    if "email" not in data:
        msg = "No email provided for person."
        logger.info(msg)
        return create_response(status=422, message=msg)

    #  create MongoEngine objects
    new_person = Person(name=data["name"], email=data["email"])
    new_person.save()

    return create_response(
        message=f"Successfully created person {new_person.name} with id: {new_person.id}"
    )
