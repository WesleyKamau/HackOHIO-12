"""
migrate_copy_to_dev.py

Copy chats from the current database into the development database and tag
all copied documents with env='dev'. This script uses upsert semantics on
`groupme_id` so it is safe to run multiple times.

Environment variables used:
- MONGODB_URI      - required, the connection URI (to the cluster that hosts both DBs)
- MONGODB_DB       - optional, source DB name (fallback)
- MONGODB_DB_DEV   - optional, destination dev DB name (fallback will be used)
- DRY_RUN          - if set to '1' the script only prints the planned actions
- TAG              - optional, env tag to apply (default 'dev')

Example usage (PowerShell):
$env:MONGODB_URI="mongodb+srv://user:pass@cluster0.xxxx.mongodb.net"; \
$env:MONGODB_DB="rhac_db"; $env:MONGODB_DB_DEV="rhac_db_dev"; python .\\backend\\migrate_copy_to_dev.py

"""

from pymongo import MongoClient, UpdateOne
import os
import sys

MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    print('MONGODB_URI is required. Set it in the environment and try again.')
    sys.exit(2)

SRC_DB = os.getenv('MONGODB_DB') or 'rhac_db'
DEST_DB = os.getenv('MONGODB_DB_DEV') or os.getenv('MONGODB_DB') or 'rhac_db_dev'
DRY_RUN = os.getenv('DRY_RUN', '') == '1'
TAG = os.getenv('TAG', 'dev')

print(f"Connecting to MongoDB URI: {MONGODB_URI}")
print(f"Source DB: {SRC_DB}")
print(f"Destination DB: {DEST_DB}")
print(f"Tagging documents with env: '{TAG}'")

client = MongoClient(MONGODB_URI)
src_db = client[SRC_DB]
dest_db = client[DEST_DB]

src_coll = src_db['chats']
dest_coll = dest_db['chats']

# Read all documents from source
print('Reading documents from source...')
docs = list(src_coll.find({}))
print(f'Found {len(docs)} documents in {SRC_DB}.chats')

if len(docs) == 0:
    print('Nothing to migrate. Exiting.')
    sys.exit(0)

# Prepare bulk upserts keyed by groupme_id to avoid duplicates
bulk_ops = []
for d in docs:
    # Build the replacement doc; keep original fields but set env
    doc = dict(d)
    doc['env'] = TAG
    # Remove _id to allow upsert using groupme_id
    doc.pop('_id', None)
    op = UpdateOne({'groupme_id': doc.get('groupme_id')}, {'$set': doc}, upsert=True)
    bulk_ops.append(op)

print(f'Prepared {len(bulk_ops)} upsert operations')
if DRY_RUN:
    print('DRY_RUN enabled; no writes will be performed.')
    sys.exit(0)

# Execute bulk writes in reasonable batches
BATCH = 500
count = 0
for i in range(0, len(bulk_ops), BATCH):
    batch = bulk_ops[i:i+BATCH]
    result = dest_coll.bulk_write(batch)
    count += result.upserted_count + result.modified_count
    print(f'Batch {i//BATCH + 1}: upserted {result.upserted_count}, modified {result.modified_count}')

print(f'Done. Total upserts/modifications: {count}')
print('Ensure you set MONGODB_DB_DEV in production/deployment envs to use the dev DB where appropriate.')
