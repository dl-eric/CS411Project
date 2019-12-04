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


@main.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")

    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return create_response(status=400)

    try:
        result = db.session.execute(
            "INSERT INTO User (username, password) VALUES (:username, :password)",
            {"username": username, "password": password},
        )
        db.session.commit()
    except IntegrityError:
        return create_response(status=409, message="User already exists")
    except Exception as e:
        return create_response(status=500, message="Something went wrong")

    # Get the userId of the user we just created so we can return it
    result = db.session.execute(
        "SELECT userId FROM User WHERE username=:username", {"username": username}
    )
    user = result.fetchone()

    return create_response(data={"userId": user.userId}, status=200)


@main.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")

    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return create_response(status=400)

    result = db.session.execute(
        "SELECT * FROM User WHERE username=:username", {"username": username}
    )
    user = result.fetchone()
    result.close()

    if user:
        if user.password == password:
            return create_response(data={"userId": user.userId})
        else:
            return create_response(status=401, message="Password incorrect")
    else:
        return create_response(status=404, message="User not found")


@main.route("/friends", methods=["GET", "POST"])
def friends():
    if request.method == "GET":
        user_id = request.args.get("userId")
        if not user_id:
            return create_response(status=400, message="Must supply userId")

        # Check if userId exists
        result = db.session.execute(
            "SELECT * FROM User WHERE userId=:userId", {"userId": user_id}
        )
        user = result.fetchone()
        result.close()

        if user:
            result = db.session.execute(
                "SELECT * FROM Friend WHERE userId=:userId", {"userId": user_id}
            )
            friends = []
            for friend in result:
                friends.append({"name": friend.name, "friendId": friend.friendId})

            return create_response(data={"friends": friends})
        else:
            return create_response(status=404, message="User does not exist")

    # We're in the POST flow. User wants to create a friend
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")

    user_id = body.get("userId")
    name = body.get("name")

    if not user_id or not name:
        return create_response(status=400)

    result = db.session.execute(
        "INSERT INTO Friend (userId, name) VALUES (:userId, :name)",
        {"userId": user_id, "name": name},
    )
    db.session.commit()
    return create_response(message="Successfully created friend")


@main.route("/friends/<id>", methods=["GET", "PUT", "DELETE"])
def friend(id):
    if request.method == "PUT":
        # We're in the PUT flow. User wants to edit the friend
        body = request.get_json()
        if not body:
            return create_response(status=400, message="Not JSON")

        name = body.get("name")

        if not name:
            return create_response(
                status=400, message="Name field needs to be supplied"
            )

        result = db.session.execute(
            "UPDATE Friend SET name=:name WHERE friendId=:id", {"name": name, "id": id}
        )
        db.session.commit()
        return create_response(status=200, message="Successfully updated friend")

    # Check if friend exists
    result = db.session.execute("SELECT * FROM Friend WHERE friendId=:id", {"id": id})
    friend = result.fetchone()

    if not friend:
        return create_response(status=404, message="Friend not found")

    if request.method == "DELETE":
        try:
            result = db.session.execute(
                "DELETE FROM Friend WHERE friendId=:id", {"id": id}
            )
            db.session.commit()
            return create_response(status=200, message="Friend successfully deleted")
        except Exception as e:
            return create_response(status=500, message="Something went wrong...")

    # We're in GET flow. User wants friend info
    friend = dict(friend.items())
    return create_response(data=friend, status=200)


@main.route("/sentiments", methods=["POST"])
def sentiments():
    body = request.get_json()
    if not body:
        return create_response(status=400, message="Not JSON")

    friend_id = body.get("friendId")
    filename = body.get("filename")

    if not friend_id or not filename:
        return create_response(
            status=400, message="friendId and filename fields need to be supplied"
        )

    try:
        result = db.session.execute(
            "INSERT INTO Sentiment (friendId, filename) VALUES (:friend_id, :filename)",
            {"friend_id": friend_id, "filename": filename},
        )
        db.session.commit()
    except IntegrityError:
        return create_response(status=400, message="Invalid friendId")
    except Exception as e:
        return create_response(status=500, message="Something went wrong...")

    return create_response(status=200, message="Successfully created sentiment")


@main.route("/messagecount/<id>", methods=["PUT", "GET"])
def get_message_count(id):
    result = db.session.execute(
        "SELECT Fr.friendId, SUM(Fi.totalMessages) as sumMessages FROM User U JOIN Friend Fr on U.userId=Fr.userId JOIN File Fi on Fr.friendId=Fi.friendId WHERE U.userId=(:id) GROUP BY Fr.friendId",
        {"id": id},
    )

    ret = [dict(row) for row in result]
    for entry in ret:
        if entry["sumMessages"] is not None:
            entry["sumMessages"] = int(entry["sumMessages"])

    return create_response(data={"counts": ret})


@main.route("/sentiments/<id>", methods=["PUT", "GET"])
def get_sentiment(id):
    if request.method == "PUT":
        # We're in the PUT flow. User wants to edit the friend
        body = request.get_json()
        if not body:
            return create_response(status=400, message="Not JSON")

        filename = body.get("filename")

        if not filename:
            return create_response(
                status=400, message="Filename field needs to be supplied"
            )

        result = db.session.execute(
            "UPDATE Sentiment SET fileName=:filename WHERE friendId=:id",
            {"filename": filename, "id": id},
        )
        db.session.commit()
        return create_response(status=200, message="Successfully updated Sentiment")

    # Check if sentiment exists
    result = db.session.execute(
        "SELECT * FROM Sentiment WHERE friendId=:id", {"id": id}
    )
    sentiment = result.fetchone()

    if not sentiment:
        return create_response(status=404, message="Sentiment not found.")

    # We're in GET flow
    sentiment = dict(sentiment.items())

    return create_response(data=sentiment, status=200)
