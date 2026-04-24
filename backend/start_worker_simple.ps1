# Simple edge worker starter with .env loading
$ErrorActionPreference = "Stop"

# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "Set $name" -ForegroundColor Gray
    }
}

Write-Host "Starting edge worker..." -ForegroundColor Green
python worker.py edge
