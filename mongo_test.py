from pymongo import MongoClient
from pprint import pprint

mongo_client = MongoClient("localhost")
db=mongo_client.admin
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)

task = db.tasks.find_one({'job': "B"})
print(task)