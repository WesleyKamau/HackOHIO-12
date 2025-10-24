from pymongo import MongoClient, errors as pymongo_errors
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_db_check():
    # Validate config (non-fatal)
    Config.validate(fail_on_missing=False)

    uri = Config.MONGODB_URI
    if not uri:
        logger.warning("MONGODB_URI not set. Skipping DB connection test.")
        return False

    try:
        logger.info("Connecting to MongoDB: %s", uri)
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info("Connected to MongoDB!")
        return True
    except pymongo_errors.PyMongoError as e:
        logger.exception("Connection failed: %s", e)
        return False


if __name__ == '__main__':
    run_db_check()
