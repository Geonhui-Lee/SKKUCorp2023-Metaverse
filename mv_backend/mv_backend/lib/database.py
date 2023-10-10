from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mv_backend.mv_backend.settings import MONGODB_CONNECTION_STRING

class Database:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING, server_api=ServerApi('1'))
    
    def get_client(self):
        return self.client

    def get_database(self, database_name):
        return self.client[database_name]

    def get_collection(self, database_name, collection_name):
        return self.get_database(database_name)[collection_name]
    
    def get_all_collections(self, database_name):
        return self.get_database(database_name).list_collection_names()
    
    def get_all_documents(self, database_name, collection_name):
        return self.get_collection(database_name, collection_name).find()
    
    def set_document(self, database_name, collection_name, document):
        return self.get_collection(database_name, collection_name).insert_one(document)
    
    def set_documents(self, database_name, collection_name, documents):
        return self.get_collection(database_name, collection_name).insert_many(documents)