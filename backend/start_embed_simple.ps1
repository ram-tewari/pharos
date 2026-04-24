$env:MODE = "EDGE"
$env:EMBEDDING_MODEL_NAME = "nomic-ai/nomic-embed-text-v1"

Write-Host "Starting embed server on port 8001..." -ForegroundColor Cyan
python -m uvicorn embed_server:app --host 127.0.0.1 --port 8001 --log-level info
