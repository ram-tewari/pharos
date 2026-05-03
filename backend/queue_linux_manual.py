#!/usr/bin/env python3
"""Manually push Linux ingestion task to ingest_queue."""
import json
import time
from datetime import datetime
from upstash_redis import Redis
import os

redis = Redis(
    url=os.getenv('UPSTASH_REDIS_REST_URL'),
    token=os.getenv('UPSTASH_REDIS_REST_TOKEN')
)

task = {
    'repo_url': 'github.com/torvalds/linux',
    'submitted_at': datetime.now().isoformat(),
    'submitted_at_unix': time.time(),
    'ttl': 86400,
    'task_id': f'linux-manual-{int(time.time())}',
    'job_id': f'linux-manual-{int(time.time())}',
    'status': 'pending',
}

redis.rpush('ingest_queue', json.dumps(task))
print(f'Pushed task to ingest_queue: {task["task_id"]}')
print(f'Queue length: {redis.llen("ingest_queue")}')
