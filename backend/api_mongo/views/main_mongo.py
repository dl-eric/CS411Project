from flask import Blueprint, request, jsonify, send_file
from api_mongo.models import db
from api.models.base import db as sqldb
from api_mongo.core import create_response, serialize_list, logger
import pymongo
import json
from bson.code import Code
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import re
from collections import Counter
import numpy as np
from requests_toolbelt import MultipartEncoder
import os
import zipfile
import datetime

main_mongo = Blueprint("main_mongo", __name__)  # initialize blueprint

with open("sentiment_dict.json") as template:
    template_dct = json.load(template)

neg = template_dct["negative"]
pos = template_dct["positive"]
neg_set = set(neg)
pos_set = set(pos)

emoji_dict = {
    "ð\x9f\x98\x8d": "\U0001F60D",
    "ð\x9f\x98\x86": "\U0001F606",
    "â\x9d¤": "\U00002764",
    "ð\x9f\x98®": "\U0001F62E",
    "ð\x9f\x98¢": "\U0001F622",
    "ð\x9f\x98\xa0": "\U0001F620",
    "ð\x9f\x91\x8d": "\U0001F44D",
    "ð\x9f\x91\x8e": "\U0001F44E",
}


def sentiment_analysis_pos(s):
    l = Counter(s)
    pos_dict = {k: v for k, v in l.items() if (k in pos_set)}
    return pos_dict


def sentiment_analysis_neg(s):
    l = Counter(s)
    neg_dict = {k: v for k, v in l.items() if (k in neg_set)}
    return neg_dict


def split_and_lower(s):
    return list(filter(lambda x: len(x) > 1, re.split("[^a-z']", s.lower())))


# insert messages into db
def insert_file(userId, friendId, fileid, filename):
    with open(filename) as template:
        template_dct = json.load(template)

    messages = template_dct["messages"]

    for message in messages:
        key = "content"
        if (key in message) and (message["type"] == "Generic"):
            content = message[key]
            message[key] = split_and_lower(content)
            message["word_count"] = len(message[key])
            message["userId"] = userId
            message["friendId"] = friendId
            message["fileid"] = fileid

    db.message.insert_many(messages)

    print("Finished insert")


def remove_user(userId):
    db.message.remove({"userId": userId})


def remove_friend(userId, friendId):
    db.message.remove({"$and": [{"userId": userId}, {"friendId": friendId}]})


def remove_file(userId, friendId, fileid):
    db.message.remove(
        {"$and": [{"userId": userId}, {"friendId": friendId}, {"fileid": fileid}]}
    )


# counts # of messages sent by each person
def message_counts(userId, friendId):
    mapper = Code(
        """
    function() {
        // derived from lecture
        for (var idx = 0; idx < this.sender_name.length; idx++) {
            var key = this.sender_name;
            var value = 1;
            emit(key, value);
        }
    };
    """
    )

    reducer = Code(
        """
    function(key, values) {
        return Array.sum(values);
    };
    """
    )

    result = db.message.map_reduce(
        mapper,
        reducer,
        "out",
        query={"$and": [{"userId": userId}, {"friendId": friendId}]},
    )

    for doc in result.find():
        print(doc)


# counts # of words sent by each person
def word_counts(userId, friendId):
    mapper = Code(
        """
    function() {
        // derived from lecture
        for (var idx = 0; idx < this.sender_name.length; idx++) {
            var key = this.sender_name;
            var value = this.word_count;
            emit(key, value);
        }
    };
    """
    )

    reducer = Code(
        """
    function(key, values) {
        return Array.sum(values);
    };
    """
    )

    result = db.message.map_reduce(
        mapper,
        reducer,
        "out",
        query={
            "$and": [
                {"word_count": {"$gt": 0}},
                {"userId": userId},
                {"friendId": friendId},
            ]
        },
    )

    for doc in result.find():
        print(doc)


# returns most frequent reacts and frequency
def frequent_reacts(userId, friendId):
    mapper = Code(
        """
    function() {
        for (var idx = 0; idx < this.reactions.length; idx++) {
            var key = this.reactions[idx].reaction;
            var value = 1;
            emit(key, value);
        }
    };
    """
    )

    reducer = Code(
        """
    function(key, values) {
        return Array.sum(values);
    };
    """
    )

    result = db.message.map_reduce(
        mapper,
        reducer,
        "out",
        query={
            "$and": [
                {"userId": userId},
                {"friendId": friendId},
                {"reactions": {"$exists": True}},
            ]
        },
    )

    emojis = []
    count = []

    for doc in result.find():
        for k, v in doc.items():
            if k == "_id":
                emojis.append(emoji_dict[v])
            else:
                count.append(v)

    print(emojis, count)
    return {"emoji": emojis, "count": count}


# sentiment analysis
def sentiment_analysis(userId, friendId):
    messages = db.message.aggregate(
        [
            {
                "$match": {
                    "$and": [
                        {"userId": userId},
                        {"friendId": friendId},
                        {"word_count": {"$gt": 0}},
                    ]
                }
            },
            {"$unwind": "$content"},
            {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}},
        ]
    )

    ret = {}

    for message in messages:
        ret[m_arr["_id"]] = {
            "pos": sentiment_analysis_pos(message["content"]),
            "neg": sentiment_analysis_neg(message["content"]),
        }

    return ret


# word cloud
def word_cloud(userId, friendId):
    messages = db.message.aggregate(
        [
            {"$match": {"userId": userId, "friendId": friendId, "type": "Generic"}},
            {"$unwind": "$content"},
            {"$group": {"_id": "$sender_name", "content": {"$push": "$content"}}},
        ]
    )
    logger.info("user %s", userId)
    logger.info("friend %s", friendId)

    ret = {}

    for m_arr in messages:
        ret[m_arr["_id"]] = Counter(m_arr["content"])
        # message = " ".join(m_arr["content"])
        # word_cloud_generator(
        #     str(userId) + "_" + str(friendId) + "_" + m_arr["_id"], message
        # )
    return ret


def find_messages_between(userId, friendId):
    messages = db.message.find({"$and": [{"userId": userId}, {"friendId": friendId}]})

    print("Number of records = " + str(messages.count()))
    for message in messages:
        print(message)


def find_messages_in_file(userId, friendId):
    messages = db.message.find({"$and": [{"userId": userId}, {"friendId": friendId}]})
    print("Number of records = " + str(messages.count()))
    for message in messages:
        print(message)


def drop_messages():
    db.message.drop()


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


@main_mongo.route("/messages/<user_id>/<friend_id>")
def get_files(user_id, friend_id):
    alice = set()
    timestamps = sqldb.session.execute(
        "SELECT timestamp FROM Friend Fr JOIN File Fi ON Fr.friendId=Fi.friendId WHERE Fr.friendId=:id",
        {"id": friend_id},
    )

    for timestamp in timestamps:
        alice.add(timestamp.timestamp)

    return create_response(data={"timestamps": list(alice)})


@main_mongo.route("/messages", methods=["POST"])
def create_messages():
    data = request.form

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sqldb.session.execute(
        "INSERT INTO File (timestamp, friendId) VALUES (:timestamp, :id)",
        {"timestamp": timestamp, "id": data["friendId"]},
    )
    sqldb.session.commit()

    c = sqldb.session.execute(
        "SELECT id FROM File WHERE timestamp=:timestamp", {"timestamp": timestamp}
    )
    file_id = c.fetchone()["id"]

    if data is None:
        return create_response(status=400, message="Form data not provided")

    for field in ["userId", "friendId"]:
        if field not in data:
            return create_response(status=400, message=field + " not provided")

    logger.info("Data recieved: %s", data)
    f = request.files.get("file")
    if f is None:
        return create_response(status=400, message="File not provided")

    file_data = json.load(f)["messages"]

    for message in file_data:
        key = "content"
        if (key in message) and (message["type"] == "Generic"):
            content = message[key]
            message[key] = split_and_lower(content)
            message["word_count"] = len(message[key])
            message["fileId"] = file_id
            message["userId"] = data["userId"]
            message["friendId"] = data["friendId"]

    db.message.insert_many(file_data)

    sqldb.session.execute(
        "UPDATE File SET totalMessages=(:totalMessages) WHERE id=(:id)",
        {"totalMessages": len(file_data), "id": file_id},
    )

    sqldb.session.commit()

    return create_response(
        message=f"Successfully created new message", data={"timestamp": timestamp}
    )


@main_mongo.route("/sentiments", methods=["GET"])
def get_sentiments():
    userId = request.args.get("userId")
    friendId = request.args.get("friendId")

    if not userId:
        return create_response(status=400, message="Must specify userId")

    if not friendId:
        return create_response(status=400, message="Must specify friendId")

    userId = str(userId)
    friendId = str(friendId)

    frequent_reacts(userId, friendId)

    counts = word_cloud(userId, friendId)

    countsOut = {}
    for key in counts.keys():
        countsOut[key] = {}
        countsOut[key]["pos"] = [
            {"text": key2, "value": counts[key][key2]}
            for key2 in counts[key].keys()
            if key2 in pos
        ]
        countsOut[key]["neg"] = [
            {"text": key2, "value": counts[key][key2]}
            for key2 in counts[key].keys()
            if key2 in neg
        ]

    return create_response(data={"counts": countsOut})

