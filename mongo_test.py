from pymongo import MongoClient
from pprint import pprint
import pandas as pd

# Can be repurposed to analyze the data instead
# Just need a venv or conda environment with pymongo, pandas and probably numpy in future
mongo_client = MongoClient("localhost")
db=mongo_client.admin
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)

for task in db.tasks.find({'parsed_id': "9c3af582"}):
    print(task['state'])

result = db.tasks.update_many({'parsed_id': "9c3af582"}, {'$set':{'state': 99}})
print(result.matched_count)
print(result.modified_count)

for task in db.tasks.find({'parsed_id': "9c3af582"}):
    print(task['state'])


df = pd.DataFrame(list(db.tasks.find({'state': {"$gte":98}})))
print("Successful:", len(df['parsed_id'].unique()))

df = pd.DataFrame(list(db.tasks.find({'state': {"$lt":98}})))
print("Failed:", len(df['parsed_id'].unique()))