from pymongo import MongoClient
from pprint import pprint

class MyMongoDBClass():
    def __init__(self, host="localhost", port=27017, db="admin", collection="tasks"):
        print("MyMongoDBClass")
        self._mongoc = MongoClient(host, port)

        self._db = self._mongoc[db]
        print(self._db)
        pass

    def insert(self, collection, payload):
        print("Insert -> {}".format(payload))
        c = self._db[collection]
        t_id = c.insert_one(payload).inserted_id
        return t_id

    def find_one(self, collection):
        # 5e4cd5d3a68938cdc24707d6
        res = self._db[collection].find_one()
        pprint(res)
        return res

    def find(self, collection, query_dict):
        # 5e4cd5d3a68938cdc24707d6
        res = self._db[collection].find(query_dict)
        pprint("Found: {}".format(self._db[collection].count_documents(query_dict)))
        return res

    def find_unsent_tasks(self):
        res = self._db["tasks"].find({'processed':None})
        return res

    def update(self, collection, id, change_dict):
        res = self._db[collection].find_one_and_update({"_id": id}, {'$set': change_dict})
        return res

    def get_db(self, db):
        return self._mongoc[db]

    def get_client(self):
        return self._mongoc