from flask import Blueprint, request, jsonify
from api_mongo.models import db
from api_mongo.core import create_response, serialize_list, logger
import json

main_mongo = Blueprint("main_mongo", __name__)  # initialize blueprint


@main_mongo.route("/test", methods=["GET"])
def test():
    return create_response(data={"items": ["hello", "world"]})


@main_mongo.route("/messages", methods=["GET"])
def get_messages():
    userId = request.args.get("userId")

    if not userId:
        return create_response(status=400, message="Must specify userId")

    # messages = Message.objects(userId=userId)
    messages = list(db.message.find({"userId": userId}, {"_id": 0}))

    # Check if userId exists in db
    if len(messages) == 0:
        return create_response(
            status=404, message="Messages of specified user id not found"
        )

    return create_response(data={"messages": messages})


@main_mongo.route("/messages", methods=["POST"])
def create_messages():
    data = request.form
    logger.info("Data recieved: %s", data)
    f = request.files.get("file")

    file_data = json.load(f)["messages"]

    for message in file_data:
        message["fileId"] = data["fileId"]
        message["userId"] = data["userId"]
        message["friendId"] = data["friendId"]

    db.message.insert_many(file_data)

    return create_response(message=f"Successfully created new message")


# function that is called when you visit /persons
@main_mongo.route("/persons", methods=["GET"])
def get_persons():
    persons = db.person.find()
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
    db.person.insert_one({"name": data["name"], "email": data["email"]})

    return create_response(
        message=f"Successfully created person {data['name']} with id: {data['email']}"
    )
