# Example Python Code to Insert a Document 

from pymongo import MongoClient 
from bson.objectid import ObjectId 

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, username, password, host, port, database, collection): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. This is hard-wired to use the aac 
        # database, the animals collection, and the aac user. 
        # 
        # You must edit the password below for your environment. 
        # 
        # Connection Variables 
        # 
        #USER = 'aacuser' 
       #PASS = 'biteof87' 
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        
        
        # 
        # Initialize Connection
        self.client = MongoClient(
        'mongodb://%s:%d/' % (HOST, PORT)
        )

        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]

    # Create a method to return the next available record number for use in the create method
            
    # Complete this create method to implement the C in CRUD. 
    def create(self, data):
        if data is None:
            return False
        try:
            self.collection.insert_one(data)
            return True
        except Exception:
            return False

    # Create method to implement the R in CRUD.
    def read(self, query):
        if query is None:
            return []
        try:
            return list(self.collection.find(query))
        except Exception:
            return []
        
    def update(self, query, new_values):
        try:
            result = self.collection.update_many(query, new_values)
            return result.modified_count
        except Exception:
            
            return False

    def delete(self, query):
        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception:
            return False