from pymongo import MongoClient, ASCENDING, DESCENDING
import pprint as pp
# from transform import Transform

client = MongoClient()

db = client.stocks
db.stocks.create_index([("abbreviation", ASCENDING)])
db.stocks.create_index([("date", DESCENDING)])

# db.add_son_manipulator(Transform())

# for doc in db.stocks.find( { "abbreviation": "AA"} ).sort( [ ("date", -1) ] ).limit(1):
#     pp.pprint(doc)