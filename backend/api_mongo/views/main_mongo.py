from flask import Blueprint, request, jsonify
from api_mongo.models import db, Person, Message
from api_mongo.core import create_response, serialize_list, logger
import json

main_mongo = Blueprint("main_mongo", __name__)  # initialize blueprint


@main_mongo.route("/test", methods=["GET"])
def test():
    return create_response(data={"items": ["hello", "world"]})


@main_mongo.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.objects()
    return create_response(data={"messages": messages})


@main_mongo.route("/messages", methods=["POST"])
def create_messages():
    data = request.form
    logger.info("Data recieved: %s", data)
    f = request.files.get("file")

    file_data = json.load(f)
    messages = []
    for message in file_data["messages"]:
        new_message = Message(
            sender=message["sender_name"],
            timestamp=message["timestamp_ms"],
            content=message["content"] if "content" in message else None,
            message_type=message["type"],
            file_id=data["file_id"],
            user_id=data["user_id"],
            friend_id=data["friend_id"],
            reactions=(message["reactions"] if "reactions" in message else None),
            share=message["share"]["link"] if "share" in data else None,
        )
        messages.append(new_message)
    Message.objects.insert(messages)

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
