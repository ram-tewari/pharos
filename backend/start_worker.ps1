# Pharos Edge Worker Launcher (PowerShell)
# Sets environment variables and starts the unified edge worker

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Pharos Unified Edge Worker" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Set environment variables
$env:MODE = "EDGE"
$env:UPSTASH_REDIS_REST_URL = "https://living-sculpin-96916.upstash.io"
$env:UPSTASH_REDIS_REST_TOKEN = "gQAAAAAAAXqUAAIncDFmMDExYmFjN2Y1ZjQ0ZDY2Yjc0NWE1NTBhMzg2ZDg5M3AxOTY5MTY"
$env:DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_2Lv8pxVJzgyd@ep-flat-meadow-ahvsmoyw-pooler.c-3.us-east-1.aws.neon.tech/neondb"
$env:EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1"
$env:DB_POOL_SIZE = "1"
$env:DB_MAX_OVERFLOW = "2"
$env:WORKER_POLL_INTERVAL = "2"
$env:MAX_QUEUE_SIZE = "10"
$env:MAX_WORKERS = "2"
$env:TASK_TTL_SECONDS = "3600"
$env:ENV = "dev"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:JWT_SECRET_KEY = "11a7da6fb545fc0d8d2ddd0ee03be15672799fa57128e0e55328d8750483bd79"
$env:PHAROS_ADMIN_TOKEN = "4bad61a35f5d570014f9fa2a74ac51c19a35e9185c6f1e2987f96e49eefd3c74"

Write-Host "  Mode             : EDGE" -ForegroundColor Green
Write-Host "  Queues (BLPOP)   : pharos:tasks, ingest_queue" -ForegroundColor Green
Write-Host "  BLPOP timeout    : 30s" -ForegroundColor Green
Write-Host "  Working dir      : $(Get-Location)" -ForegroundColor Green
Write-Host "  Python           : $(python --version 2>&1)" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the worker via worker.py — it patches platform.uname before any
# app import so Python 3.13 + Windows WMI doesn't hang.
python worker.py
