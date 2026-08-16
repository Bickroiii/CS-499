# Example Python Code to Insert a Document 

from pymongo import MongoClient 
from pymongo.errors import PyMongoError

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, username, password, host, port, database, collection): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. 

        
        
       # Initialize the MongoDB connection using the values provided
       # by the dashboard.
        

        if not host:
            raise ValueError("A MongoDB host is required.")

        if not database:
            raise ValueError("A MongoDB database name is required.")

        if not collection:
            raise ValueError("A MongoDB collection name is required.")

        try:
            port = int(port)
        except (TypeError, ValueError):
            raise ValueError("The MongoDB port must be a valid integer.")

        # Use authentication when both credentials are provided.
        if username and password:
            self.client = MongoClient(
                host=host,
                port=port,
                username=username,
                password=password,
                authSource=database,
                serverSelectionTimeoutMS=5000
            )

        # Allow a local MongoDB connection without authentication.
        elif not username and not password:
            self.client = MongoClient(
                host=host,
                port=port,
                serverSelectionTimeoutMS=5000
            )

        else:
            raise ValueError(
                "Both the MongoDB username and password must be provided."
            )

        self.database = self.client[database]
        self.collection = self.database[collection]

    # Create a method to return the next available record number for use in the create method
            
    # Complete this create method to implement the C in CRUD. 
    def create(self, data):
        if not isinstance(data, dict) or not data:
            return False

        try:
            result = self.collection.insert_one(data)
            return result.acknowledged

        except PyMongoError as error:
            print("Create operation failed:", error)
            return False

    # Create method to implement the R in CRUD.
    def read(self, query):
        if query is None:
            query = {}

        if not isinstance(query, dict):
            return []

        try:
            return list(self.collection.find(query))

        except PyMongoError as error:
            print("Read operation failed:", error)
            return []
        
    def update(self, query, new_values):
        # Prevent an empty query from updating the entire collection.
        if not isinstance(query, dict) or not query:
            print("Update rejected: A specific query is required.")
            return 0

        if not isinstance(new_values, dict) or not new_values:
            print("Update rejected: New values are required.")
            return 0

        # Add $set when regular field values are provided.
        if not any(key.startswith("$") for key in new_values):
            new_values = {"$set": new_values}

        try:
            result = self.collection.update_many(query, new_values)
            return result.modified_count

        except PyMongoError as error:
            print("Update operation failed:", error)
            return 0

    def delete(self, query):
        # Prevent an empty query from deleting the entire collection.
        if not isinstance(query, dict) or not query:
            print("Delete rejected: A specific query is required.")
            return 0

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count

        except PyMongoError as error:
            print("Delete operation failed:", error)
            return 0

    def close(self):
        #Close the MongoDB connection.

        self.client.close()