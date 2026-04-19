# NSSM Windows Service Configuration

This document describes the Windows service configuration for the Neo Alexandria Edge Worker using NSSM (Non-Sucking Service Manager).

## Prerequisites

- NSSM installed (download from https://nssm.cc/download or install via Chocolatey: `choco install nssm`)
- Python 3.8+ installed
- Edge worker dependencies installed (`pip install -r requirements-edge.txt`)
- `.env.edge` file configured with credentials

## Automatic Installation

The easiest way to install the service is to run the setup script:

```powershell
.\setup_edge.ps1
```

The script will:
1. Check Python and CUDA availability
2. Create virtual environment
3. Install dependencies
4. Optionally install as Windows service using NSSM

## Manual Installation

If you prefer to install the service manually:

### 1. Install NSSM

**Via Chocolatey:**
```powershell
choco install nssm -y
```

**Manual Download:**
1. Download from https://nssm.cc/download
2. Extract to a folder (e.g., `C:\nssm`)
3. Add to PATH or use full path to nssm.exe

### 2. Install Services

There are three Pharos NSSM services. Adjust the base path to match your
machine (`C:\Users\rooma\PycharmProjects\pharos\backend`).

#### PharosEdgeWorker — ingestion worker

Polls Upstash Redis for ingestion tasks and runs the full pipeline
(fetch → embed → store) on the local GPU.

```powershell
$base = "C:\Users\rooma\PycharmProjects\pharos\backend"
$py   = "$base\.venv\Scripts\python.exe"

nssm install PharosEdgeWorker $py "worker.py edge"
nssm set PharosEdgeWorker AppDirectory    $base
nssm set PharosEdgeWorker DisplayName     "Pharos Edge Ingestion Worker"
nssm set PharosEdgeWorker Description     "GPU-accelerated ingestion worker — polls Upstash Redis, embeds documents, writes to NeonDB"
nssm set PharosEdgeWorker Start           SERVICE_AUTO_START
nssm set PharosEdgeWorker AppEnvironmentExtra "MODE=EDGE"
nssm set PharosEdgeWorker AppStdout       "$base\logs\edge_worker.log"
nssm set PharosEdgeWorker AppStderr       "$base\logs\edge_worker.error.log"
nssm set PharosEdgeWorker AppRotateFiles  1
nssm set PharosEdgeWorker AppRotateBytes  10485760
nssm start PharosEdgeWorker
```

#### PharosRepoWorker — GitHub repository ingestion worker

Polls Upstash Redis `ingest_queue` for repository ingestion tasks and runs the
full workflow (clone → AST parse → embed → store → convert) locally.

```powershell
$base = "C:\Users\rooma\PycharmProjects\pharos\backend"
$py   = "$base\.venv\Scripts\python.exe"

nssm install PharosRepoWorker $py "worker.py repo"
nssm set PharosRepoWorker AppDirectory    $base
nssm set PharosRepoWorker DisplayName     "Pharos Repo Ingestion Worker"
nssm set PharosRepoWorker Description     "GitHub repository ingestion worker — clones repos, AST-parses, embeds, writes to NeonDB"
nssm set PharosRepoWorker Start           SERVICE_AUTO_START
nssm set PharosRepoWorker AppEnvironmentExtra "MODE=EDGE"
nssm set PharosRepoWorker AppStdout       "$base\logs\repo_worker.log"
nssm set PharosRepoWorker AppStderr       "$base\logs\repo_worker.error.log"
nssm set PharosRepoWorker AppRotateFiles  1
nssm set PharosRepoWorker AppRotateBytes  10485760
nssm start PharosRepoWorker
```

#### PharosEmbedServer — HTTP embedding server

Loads `nomic-ai/nomic-embed-text-v1` on the GPU and serves
`POST /embed` on `127.0.0.1:8001`. Tailscale Funnel proxies this port
to a public `*.ts.net` HTTPS endpoint that Render calls during search.

```powershell
$base = "C:\Users\rooma\PycharmProjects\pharos\backend"
$py   = "$base\.venv\Scripts\python.exe"

nssm install PharosEmbedServer $py "-m uvicorn embed_server:app --host 127.0.0.1 --port 8001"
nssm set PharosEmbedServer AppDirectory    $base
nssm set PharosEmbedServer DisplayName     "Pharos Edge Embedding Server"
nssm set PharosEmbedServer Description     "FastAPI server exposing POST /embed for query embeddings; called by Render via Tailscale Funnel"
nssm set PharosEmbedServer Start           SERVICE_AUTO_START
nssm set PharosEmbedServer AppEnvironmentExtra "MODE=EDGE"
nssm set PharosEmbedServer AppStdout       "$base\logs\embed_server.log"
nssm set PharosEmbedServer AppStderr       "$base\logs\embed_server.error.log"
nssm set PharosEmbedServer AppRotateFiles  1
nssm set PharosEmbedServer AppRotateBytes  10485760
nssm start PharosEmbedServer
```

Verify it started:
```powershell
nssm status PharosEmbedServer
curl http://127.0.0.1:8001/health
# {"status": "ok", "model": "nomic-ai/nomic-embed-text-v1"}
```

#### PharosTailscaleFunnel — Funnel persistence fallback (optional)

Tailscale Funnel configuration persists in `tailscaled` state by default
and re-applies on daemon restart. **Run `tailscale funnel 8001` once manually,
reboot, then check `tailscale funnel status`.**

Only install this NSSM service if the Funnel rule does not survive a reboot:

```powershell
# Find tailscale.exe — typically:
$ts = "C:\Program Files\Tailscale\tailscale.exe"

nssm install PharosTailscaleFunnel $ts "funnel 8001"
nssm set PharosTailscaleFunnel DisplayName "Pharos Tailscale Funnel (port 8001)"
nssm set PharosTailscaleFunnel Description "Keeps Tailscale Funnel active for PharosEmbedServer on port 8001"
nssm set PharosTailscaleFunnel Start       SERVICE_AUTO_START
nssm set PharosTailscaleFunnel AppStdout   "C:\Users\rooma\PycharmProjects\pharos\backend\logs\tailscale_funnel.log"
nssm start PharosTailscaleFunnel
```

### 3. Start Services

```powershell
nssm start PharosEdgeWorker
nssm start PharosEmbedServer
# PharosTailscaleFunnel only if needed (see above)
```

## Service Management Commands

### Start Service
```powershell
nssm start NeoAlexandriaWorker
```

### Stop Service
```powershell
nssm stop NeoAlexandriaWorker
```

### Restart Service
```powershell
nssm restart NeoAlexandriaWorker
```

### Check Status
```powershell
nssm status NeoAlexandriaWorker
```

### View Logs
```powershell
# View last 50 lines and follow
Get-Content worker.log -Tail 50 -Wait

# View error log
Get-Content worker.error.log -Tail 50 -Wait
```

### Edit Service Configuration
```powershell
nssm edit NeoAlexandriaWorker
```

This opens a GUI where you can modify service settings.

### Remove Service
```powershell
nssm stop NeoAlexandriaWorker
nssm remove NeoAlexandriaWorker confirm
```

## Service Configuration Details

| Service | Executable | Arguments | Port | Purpose |
|---------|-----------|-----------|------|---------|
| `PharosEdgeWorker` | `.venv\Scripts\python.exe` | `worker.py edge` | — | Edge ingestion pipeline (polls pharos:tasks) |
| `PharosRepoWorker` | `.venv\Scripts\python.exe` | `worker.py repo` | — | GitHub repo ingestion (polls ingest_queue) |
| `PharosEmbedServer` | `.venv\Scripts\python.exe` | `-m uvicorn embed_server:app --host 127.0.0.1 --port 8001` | 8001 | Query embedding HTTP server |
| `PharosTailscaleFunnel` | `tailscale.exe` | `funnel 8001` | — | Funnel persistence fallback only |

All services: `Start=SERVICE_AUTO_START`, log rotation at 10 MB, NSSM restart on failure.

## Troubleshooting

### Service Won't Start

1. Check logs:
   ```powershell
   Get-Content worker.error.log -Tail 50
   ```

2. Verify Python path:
   ```powershell
   nssm get NeoAlexandriaWorker Application
   ```

3. Test worker manually:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python worker.py
   ```

### Service Starts But Doesn't Work

1. Check environment variables:
   ```powershell
   nssm get NeoAlexandriaWorker AppEnvironmentExtra
   ```

2. Verify `.env.edge` file exists and has correct credentials

3. Check Redis connectivity:
   ```powershell
   python -c "from upstash_redis import Redis; import os; from dotenv import load_dotenv; load_dotenv('.env.edge'); r = Redis(url=os.getenv('UPSTASH_REDIS_URL'), token=os.getenv('UPSTASH_REDIS_TOKEN')); print(r.ping())"
   ```

### High Memory Usage

The worker loads PyTorch and GPU models, which requires significant memory:
- Minimum: 4GB RAM
- Recommended: 8GB+ RAM
- GPU: 8GB+ VRAM for optimal performance

### Service Crashes on Startup

1. Check if another instance is running:
   ```powershell
   Get-Process python | Where-Object {$_.Path -like "*neo-alexandria*"}
   ```

2. Verify CUDA drivers (if using GPU):
   ```powershell
   nvidia-smi
   ```

3. Check for port conflicts (if worker uses ports)

## Log Rotation

NSSM automatically rotates logs when they reach 10MB. Old logs are renamed with a `.1`, `.2`, etc. suffix.

To change rotation size:
```powershell
nssm set NeoAlexandriaWorker AppRotateBytes 20971520  # 20MB
```

To disable rotation:
```powershell
nssm set NeoAlexandriaWorker AppRotateFiles 0
```

## Running Multiple Workers

To run multiple workers (e.g., for different projects):

```powershell
# Install second worker
nssm install NeoAlexandriaWorker2 "C:\path\to\.venv\Scripts\python.exe" "worker.py"
nssm set NeoAlexandriaWorker2 AppDirectory "C:\path\to\backend"
nssm set NeoAlexandriaWorker2 AppEnvironmentExtra "MODE=EDGE"

# Use different .env file
nssm set NeoAlexandriaWorker2 AppEnvironmentExtra "ENV_FILE=.env.edge2"
```

## Security Considerations

1. **Run as Limited User**: Don't run as Administrator
   ```powershell
   nssm set NeoAlexandriaWorker ObjectName ".\LimitedUser" "password"
   ```

2. **Protect Credentials**: Ensure `.env.edge` has restricted permissions
   ```powershell
   icacls .env.edge /inheritance:r /grant:r "$env:USERNAME:(R)"
   ```

3. **Monitor Logs**: Regularly check logs for errors or suspicious activity

## Performance Tuning

### GPU Optimization

Set environment variables for optimal GPU usage:
```powershell
nssm set NeoAlexandriaWorker AppEnvironmentExtra "CUDA_VISIBLE_DEVICES=0"
nssm set NeoAlexandriaWorker AppEnvironmentExtra "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512"
```

### CPU Affinity

Limit CPU cores used by worker:
```powershell
nssm set NeoAlexandriaWorker AppAffinity 0x0F  # Use first 4 cores
```

### Process Priority

Set process priority (use with caution):
```powershell
nssm set NeoAlexandriaWorker AppPriority ABOVE_NORMAL_PRIORITY_CLASS
```

## Uninstallation

To completely remove the service:

```powershell
# Stop service
nssm stop NeoAlexandriaWorker

# Remove service
nssm remove NeoAlexandriaWorker confirm

# Clean up logs (optional)
Remove-Item worker.log, worker.error.log
```

## Additional Resources

- NSSM Documentation: https://nssm.cc/usage
- Windows Services: https://docs.microsoft.com/en-us/windows/win32/services/services
- Neo Alexandria Documentation: See `backend/docs/`
