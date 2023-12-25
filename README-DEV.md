# MongoDB

## Distinct

db = db.getSiblingDB("sheena-ba");
db.getCollection("github_pr").distinct("identifier");
db.getCollection("github_repository").distinct("identifier");

or 

db.github_pr.distinct("identifier);


## Count

count = db.github_pr.count_documents({"identifier": "hello"})

## Group Count

counts = db.github_pr.aggregate([
    {"$group": {"_id": "$identifier", "count": {"$sum": 1}}}
])