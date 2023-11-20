from pymongo import MongoClient
from ..core.logger import log

log.debug("Connect to MongoDB")
_client = MongoClient("localhost", 9017)
_db = _client["sheena-ba"]

# export
mdb = _db
