from api_mongo.core import Mixin
from .base import db
from api_mongo.models import Email
from flask_mongoengine import Document
from mongoengine import *


class Person(Document, Mixin):
    """Person Collection."""

    name = StringField(required=True)
    email = StringField(required=True)

    # def __init__(self, name: str):
    #     self.name = name

    def __repr__(self):
        return f"<Person {self.name}>"
