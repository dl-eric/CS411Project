from flask_mongoengine import MongoEngine
from pymongo import MongoClient
import os

# instantiate database object
#db = MongoEngine()
db = MongoClient(os.environ.get('MONGO_URL'))
db = db['cs411-final-project']