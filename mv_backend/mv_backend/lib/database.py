from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from mv_backend.settings import MONGODB_CONNECTION_STRING

class Database:
    def __init__(self, unique_id=None):
        self.client = MongoClient(MONGODB_CONNECTION_STRING, server_api=ServerApi('1'))
        self.uid = unique_id
    
    def get_uid(self):
        return self.uid
    
    def set_uid(self, unique_id=None):
        self.uid = unique_id

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
    
    def get_all_documents_of_user(self, database_name, collection_name):
        if (self.uid != None):
            return self.get_all_documents_by_query(database_name, collection_name, {'@uid': self.uid})
        else:
            return None

    def get_all_documents_by_query(self, database_name, collection_name, query):
        if (self.uid == None):
            return self.get_collection(database_name, collection_name).find(query)
        else:
            return self.get_collection(database_name, collection_name).find({'$and': [{'@uid': self.uid}, query]})

    def set_document(self, database_name, collection_name, document):
        return self.get_collection(database_name, collection_name).insert_one(document)
    
    def set_document_of_user(self, database_name, collection_name, document):
        if (self.uid != None):
            document['@uid'] = self.uid
            return self.set_document(database_name, collection_name, document)
        else:
            return None
    
    def set_documents(self, database_name, collection_name, documents):
        return self.get_collection(database_name, collection_name).insert_many(documents)
    
    def set_documents_of_user(self, database_name, collection_name, documents):
        if (self.uid != None):
            for document in documents:
                document['@uid'] = self.uid
            return self.set_documents(database_name, collection_name, documents)
        else:
            return None