#!/bin/bash
# backup_and_cleanup.sh - Backup and cleanup low-quality resources
#
# Usage: ./backup_and_cleanup.sh [--keep-backups N]
#
# This script:
# 1. Creates a backup of all resources
# 2. Finds low-quality resources
# 3. Offers to delete them (with confirmation)

set -e

# Configuration
KEEP_BACKUPS="${1:-5}"
BACKUP_DIR="./backups"
THRESHOLD=0.3

echo "=========================================="
echo "Pharos Backup and Cleanup"
echo "=========================================="
echo "Quality Threshold: $THRESHOLD"
echo "Backups to Keep: $KEEP_BACKUPS"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup..."
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).json"
pharos backup --output "$BACKUP_FILE"
echo "Backup saved to: $BACKUP_FILE"

# Verify backup
echo ""
echo "Verifying backup..."
if pharos backup verify "$BACKUP_FILE"; then
    echo "Backup verified successfully"
else
    echo "Warning: Backup verification failed"
fi

# Find low-quality resources
echo ""
echo "Finding low-quality resources (score < $THRESHOLD)..."
pharos quality outliers --min-score "$THRESHOLD" --format json > /tmp/low_quality.json

TOTAL=$(jq '.total' /tmp/low_quality.json)
echo "Found $TOTAL low-quality resources"

if [ "$TOTAL" -gt 0 ]; then
    echo ""
    echo "Low-quality resources:"
    jq -r '.outliers[] | "\(.resource_id): \(.quality_overall // 0)"' /tmp/low_quality.json | head -20
    
    if [ "$TOTAL" -gt 20 ]; then
        echo "... and $((TOTAL - 20)) more"
    fi
    
    echo ""
    read -p "Delete these resources? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        IDS=$(jq -r '.outliers[].resource_id' /tmp/low_quality.json | tr '\n' ',' | sed 's/,$//')
        pharos batch delete "$IDS" --force
        echo "Deleted $TOTAL low-quality resources"
    else
        echo "Skipped deletion"
    fi
else
    echo "No low-quality resources found"
fi

# Cleanup old backups
echo ""
echo "Cleaning up old backups..."
ls -1t "$BACKUP_DIR"/backup_*.json | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm
echo "Kept latest $KEEP_BACKUP backups"

# Summary
echo ""
echo "=========================================="
echo "Backup and Cleanup Complete"
echo "=========================================="
echo "Backup: $BACKUP_FILE"
echo "Resources deleted: ${TOTAL:-0}"
echo ""
echo "Current backups:"
ls -lh "$BACKUP_DIR"/backup_*.json