#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script wrangles the data and transforms the OpenStreetMap data
into dictionaries, loads them into a mongodb database and queries
the database

"""

'''
mongoimport -d examples -c waterloo --file waterloo-region_canada.json
'''

import json
import pprint

from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client.examples

#Print Postal Codes ordered by descending count
result =  db.waterloo.aggregate([{"$match" : {"address.postcode" : {"$exists" : 1}}},
						{"$group" : {"_id" : "$address.postcode",
						"count" : {"$sum" : 1}}},
						{"$sort" : {"count" : -1}}])
for item in result:
	pprint.pprint(item)


#Number of documents
documents = db.waterloo.find().count()
pprint.pprint(documents)

#Number of nodes
nodes = db.waterloo.find({"type" : "node"}).count()
pprint.pprint(nodes)

#Number of ways
ways = db.waterloo.find({"type" : "way"}).count()
pprint.pprint(ways)

#Number of unique users

#Ref: http://stackoverflow.com/questions/11782566/mongodb-select-countdistinct-x-on-an-indexed-column-count-unique-results-for
unique_users =  db.waterloo.aggregate([{ "$group": { "_id": "$created.user"}},
    {"$group": {"_id": 1, "count": { "$sum": 1}}}])
for item in unique_users:
	pprint.pprint(item)


#NO INFO ABOUT AMENITIES
