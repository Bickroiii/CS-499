# Example Python Code to Insert a Document 
from datetime import datetime, timezone

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

        # Separate collection for administrative audit records.
        self.audit_collection = self.database[
            "animal_audit_logs"
        ]

    def _write_audit_log(
        self,
        action,
        status,
        affected_count=0,
        query=None,
        details=None
    ):
        """
        Store an administrative audit record.

        Audit records do not contain passwords or database credentials.
        """

        audit_record = {
            "timestamp": datetime.now(timezone.utc),
            "action": action,
            "status": status,
            "target_collection": self.collection.name,
            "affected_count": int(affected_count)
        }

        if query is not None:
            audit_record["query"] = query

        if details is not None:
            audit_record["details"] = details

        try:
            self.audit_collection.insert_one(
                audit_record
            )
            return True

        except PyMongoError as error:
            print("Audit logging failed:", error)
            return False

    def create_indexes(self):
        """
        Create indexes used by the dashboard queries and audit collection.

        MongoDB will reuse an existing index when the same named index
        has already been created.
        """

        try:
            index_names = []

            # Supports rescue candidate searches by animal type,
            # sex, breed, and age.
            index_names.append(
                self.collection.create_index(
                    [
                        ("animal_type", ASCENDING),
                        ("sex_upon_outcome", ASCENDING),
                        ("breed", ASCENDING),
                        (
                            "age_upon_outcome_in_weeks",
                            ASCENDING
                        )
                    ],
                    name="rescue_candidate_lookup_idx"
                )
            )

            # Supports aggregation and direct lookup by animal ID.
            index_names.append(
                self.collection.create_index(
                    [
                        ("animal_id", ASCENDING)
                    ],
                    name="animal_id_lookup_idx"
                )
            )

            # Supports reviewing audit entries by date and action.
            index_names.append(
                self.audit_collection.create_index(
                    [
                        ("timestamp", DESCENDING),
                        ("action", ASCENDING)
                    ],
                    name="audit_timestamp_action_idx"
                )
            )

            self._write_audit_log(
                action="ensure_indexes",
                status="success",
                affected_count=len(index_names),
                details={
                    "indexes": index_names
                }
            )

            return index_names

        except PyMongoError as error:
            print("Index creation failed:", error)

            self._write_audit_log(
                action="ensure_indexes",
                status="failed",
                details={
                    "error": str(error)
                }
            )

            return []

            
    # Complete this create method to implement the C in CRUD.
    def create(self, data):
        if not isinstance(data, dict) or not data:
            self._write_audit_log(
                action="create",
                status="rejected",
                details={
                    "reason": "Invalid or empty document"
                }
            )

            return False

        try:
            result = self.collection.insert_one(
                data
            )

            self._write_audit_log(
                action="create",
                status="success",
                affected_count=1,
                details={
                    "inserted_id": str(
                        result.inserted_id
                    )
                }
            )

            return result.acknowledged

        except PyMongoError as error:
            print("Create operation failed:", error)

            self._write_audit_log(
                action="create",
                status="failed",
                details={
                    "error": str(error)
                }
            )

            return False

    # Create method to implement the R in CRUD.
    def read(self, query):
        if query is None:
            query = {}

        if not isinstance(query, dict):
            return []

        try:
            return list(
                self.collection.find(query)
            )

        except PyMongoError as error:
            print("Read operation failed:", error)
            return []

    def aggregate_outcome_counts(
        self,
        animal_ids=None
    ):
        """
        Use a MongoDB aggregation pipeline to count outcome types.

        When animal IDs are provided, only those table records are
        included in the aggregation.
        """

        pipeline = []

        if animal_ids is not None:
            if not isinstance(
                animal_ids,
                (list, tuple, set)
            ):
                return []

            cleaned_ids = [
                animal_id
                for animal_id in animal_ids
                if animal_id is not None
                and str(animal_id).strip()
            ]

            # Prevent an empty ID list from aggregating the entire
            # collection unexpectedly.
            if not cleaned_ids:
                return []

            # Remove duplicate IDs while preserving their order.
            cleaned_ids = list(
                dict.fromkeys(cleaned_ids)
            )

            pipeline.append(
                {
                    "$match": {
                        "animal_id": {
                            "$in": cleaned_ids
                        }
                    }
                }
            )

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {
                            "$ifNull": [
                                "$outcome_type",
                                "Unknown"
                            ]
                        },
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1,
                        "_id": 1
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "Outcome Type": "$_id",
                        "Count": "$count"
                    }
                }
            ]
        )

        try:
            return list(
                self.collection.aggregate(
                    pipeline
                )
            )

        except PyMongoError as error:
            print(
                "Outcome aggregation failed:",
                error
            )

            return []

    def aggregate_breed_counts(
        self,
        query=None,
        limit=5
    ):
        """
        Use a MongoDB aggregation pipeline to identify the most
        common breeds matching a query.
        """

        if query is None:
            query = {}

        if not isinstance(query, dict):
            return []

        try:
            limit = int(limit)

        except (TypeError, ValueError):
            limit = 5

        if limit <= 0:
            limit = 5

        pipeline = []

        if query:
            pipeline.append(
                {
                    "$match": query
                }
            )

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": {
                            "$ifNull": [
                                "$breed",
                                "Unknown"
                            ]
                        },
                        "count": {
                            "$sum": 1
                        }
                    }
                },
                {
                    "$sort": {
                        "count": -1,
                        "_id": 1
                    }
                },
                {
                    "$limit": limit
                },
                {
                    "$project": {
                        "_id": 0,
                        "breed": "$_id",
                        "count": 1
                    }
                }
            ]
        )

        try:
            return list(
                self.collection.aggregate(
                    pipeline
                )
            )

        except PyMongoError as error:
            print(
                "Breed aggregation failed:",
                error
            )

            return []

    def update(self, query, new_values):
        # Prevent an empty query from updating the entire collection.
        if not isinstance(query, dict) or not query:
            print(
                "Update rejected: A specific query is required."
            )

            self._write_audit_log(
                action="update",
                status="rejected",
                query=query,
                details={
                    "reason": (
                        "A specific query is required"
                    )
                }
            )

            return 0

        if (
            not isinstance(new_values, dict)
            or not new_values
        ):
            print(
                "Update rejected: New values are required."
            )

            self._write_audit_log(
                action="update",
                status="rejected",
                query=query,
                details={
                    "reason": (
                        "New values are required"
                    )
                }
            )

            return 0

        # Add $set when regular field values are provided.
        if not any(
            key.startswith("$")
            for key in new_values
        ):
            new_values = {
                "$set": new_values
            }

        update_fields = []

        for update_operation in new_values.values():
            if isinstance(
                update_operation,
                dict
            ):
                update_fields.extend(
                    update_operation.keys()
                )

        try:
            result = self.collection.update_many(
                query,
                new_values
            )

            self._write_audit_log(
                action="update",
                status="success",
                affected_count=result.modified_count,
                query=query,
                details={
                    "matched_count": (
                        result.matched_count
                    ),
                    "updated_fields": update_fields
                }
            )

            return result.modified_count

        except PyMongoError as error:
            print("Update operation failed:", error)

            self._write_audit_log(
                action="update",
                status="failed",
                query=query,
                details={
                    "error": str(error)
                }
            )

            return 0

    def delete(self, query):
        # Prevent an empty query from deleting the entire collection.
        if not isinstance(query, dict) or not query:
            print(
                "Delete rejected: A specific query is required."
            )

            self._write_audit_log(
                action="delete",
                status="rejected",
                query=query,
                details={
                    "reason": (
                        "A specific query is required"
                    )
                }
            )

            return 0

        try:
            result = self.collection.delete_many(
                query
            )

            self._write_audit_log(
                action="delete",
                status="success",
                affected_count=result.deleted_count,
                query=query
            )

            return result.deleted_count

        except PyMongoError as error:
            print("Delete operation failed:", error)

            self._write_audit_log(
                action="delete",
                status="failed",
                query=query,
                details={
                    "error": str(error)
                }
            )

            return 0

    def read_audit_logs(self, limit=10):
        """Return the newest administrative audit records."""

        try:
            limit = int(limit)

        except (TypeError, ValueError):
            limit = 10

        if limit <= 0:
            limit = 10

        try:
            return list(
                self.audit_collection.find({})
                .sort(
                    "timestamp",
                    DESCENDING
                )
                .limit(limit)
            )

        except PyMongoError as error:
            print(
                "Audit log read failed:",
                error
            )

            return []

    def close(self):
        """Close the MongoDB connection."""

        self.client.close()