"""Configuring Database"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = str(os.getenv("MONGO_DBNAME"))

connection = MongoClient("mongodb://mongodb:27017")
db = connection[MONGO_DBNAME]

acc_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "password"],
        "properties": {
            "username": {"bsonType": "string"},
            "password": {"bsonType": "string"},
            "messages": {"bsonType": "string"},
        },
    }
}

mess_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["message"],
        "properties": {
            "message": {"bsonType": "string"},
        },
    }
}

rec_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["filename", "audioData"],
        "properties": {
            "filename": {"bsonType": "string"},
            "audioData": {"bsonType": "binData"},
        },
    }
}


accounts = db.accounts
messages = db.messages
recordings = db.recordings

# db.command('collMod', 'accounts', validator=acc_validator)
# db.command('collMod', 'messages', validator=mess_validator)
