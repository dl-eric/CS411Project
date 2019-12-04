from api_mongo.core import Mixin
from .base import db
from flask_mongoengine import Document
from mongoengine import *


class Message(Document, Mixin):
    """Person Collection."""

    sender = StringField(required=True)
    timestamp = IntField(required=True)
    content = StringField(required=True)
    message_type = StringField(required=True)
    file_id = StringField(required=True)
    user_id = StringField(required=True)
    friend_id = StringField(required=True)
    reactions = ListField(StringField(), required=False)

    # def __init__(self, name: str):
    #     self.name = name

    def __repr__(self):
        return f"<Message {self.sender}>"
