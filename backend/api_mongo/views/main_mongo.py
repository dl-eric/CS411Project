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


def split_and_lower(s):
    return list(filter(None, re.split("[^a-z']", s.lower())))


def bar_plot_generator(title, bars, height):
    y_pos = np.arange(len(bars))
    fig = plt.figure()
    plt.bar(y_pos, height)
    plt.xticks(y_pos, bars)
    plt.title(title)
    fig.savefig(os.path.join("files", title + " bar" + ".png"))
    # plt.clt()


def word_cloud_generator(title, word_list):
    if len(word_list) > 0:
        wordcloud = WordCloud(background_color="black", colormap="rainbow").generate(
            word_list
        )
        fig = plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.title(title)
        plt.axis("off")
        fig.savefig(os.path.join("files", title + " wc" + ".png"))
    # plt.clt()


def sentiment_analysis_np(userId, friendId, sender, s):
    with open("sentiment_dict.json") as template:
        template_dct = json.load(template)
    neg = template_dct["negative"]
    pos = template_dct["positive"]

    pos_list = list((Counter(s) & Counter(pos)).elements())
    neg_list = list((Counter(s) & Counter(neg)).elements())

    # Create bar plot
    height = [len(pos_list), len(neg_list)]
    bars = ("Positive", "Negative")

    # Create word cloud
    word_cloud_generator(
        str(userId) + str(friendId) + sender + " +", " ".join(pos_list)
    )
    word_cloud_generator(
        str(userId) + str(friendId) + sender + " -", " ".join(neg_list)
    )


def split_and_lower(s):
    return list(filter(None, re.split("[^a-z']", s.lower())))


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
    return bar_plot_generator("Frequent Reacts", emojis, count)


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

    for message in messages:
        sentiment_analysis_np(userId, friendId, message["_id"], message["content"])


# word cloud
def word_cloud(userId, friendId):
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

    for m_arr in messages:
        message = " ".join(m_arr["content"])
        word_cloud_generator(str(userId) + str(friendId) + m_arr["_id"], message)


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

@main_mongo.route('/messages/<user_id>/<friend_id>')
def get_files(user_id, friend_id):
    c = db.message.find({'userId': user_id, 'friendId': friend_id}, {'timestamp': 1})

    return create_response(data={"files": list(c)})

@main_mongo.route("/messages", methods=["POST"])
def create_messages():
    data = request.form

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sqldb.session.execute(
        "INSERT INTO File (timestamp) VALUES (:timestamp)", {"timestamp": timestamp}
    )
    sqldb.session.commit()

    c = sqldb.session.execute(
        "SELECT id FROM File WHERE timestamp=:timestamp", {"timestamp": timestamp}
    )
    file_id = c.fetchone()["id"]

    if data is None:
        return create_response(status=400, message="Form data not provided")

    for field in ["fileId", "userId", "friendId"]:
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

    return create_response(message=f"Successfully created new message", data={'timestamp':timestamp})


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


@main_mongo.route("/sentiments", methods=["GET"])
def get_sentiments():
    userId = request.args.get("userId")
    friendId = request.args.get("friendId")

    if not userId:
        return create_response(status=400, message="Must specify userId")

    if not friendId:
        return create_response(status=400, message="Must specify friendId")

    message_counts(friendId, userId)
    word_counts(friendId, userId)
    frequent_reacts(friendId, userId)

    word_cloud(friendId, userId)
    sentiment_analysis(friendId, userId)

    # multi = MultipartEncoder(
    #     {"reactFile": (freq_react_file, open(freq_react_file), "text/plain")}
    # )

    # Response(m.to_string(), mimetype=m.content_type)

    # send_from

    zipf = zipfile.ZipFile("files.zip", "w", zipfile.ZIP_DEFLATED)
    zipdir("files/", zipf)
    zipf.close()

    return send_file("../files.zip")

