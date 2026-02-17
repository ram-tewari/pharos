#!/bin/bash
# find_similar.sh - Find similar resources to a given resource
#
# Usage: ./find_similar.sh <resource_id> [--limit N]
#
# This script finds resources similar to the given resource
# and optionally adds them to a collection.

set -e

RESOURCE_ID="$1"
LIMIT="${2:-10}"
COLLECTION_NAME="Similar to Resource $1"

if [ -z "$RESOURCE_ID" ]; then
    echo "Usage: $0 <resource_id> [limit]"
    echo ""
    echo "Example:"
    echo "  ./find_similar.sh 123"
    echo "  ./find_similar.sh 123 20"
    exit 1
fi

echo "=========================================="
echo "Find Similar Resources"
echo "=========================================="
echo "Resource ID: $RESOURCE_ID"
echo "Limit: $LIMIT"
echo ""

# Get resource details
echo "Resource details:"
pharos resource get "$RESOURCE_ID" --format json | jq '{title, type, quality_score}'

echo ""
echo "Finding similar resources..."

# Get similar resources
pharos recommend similar "$RESOURCE_ID" --limit "$LIMIT" --format json > /tmp/similar.json

# Display results
TOTAL=$(jq '.total' /tmp/similar.json)
echo "Found $TOTAL similar resources"

if [ "$TOTAL" -gt 0 ]; then
    echo ""
    echo "Similar resources:"
    jq -r '.recommendations[] | "  [\(.resource_id)] \(.title) (score: \(.similarity_score))"' /tmp/similar.json
    
    echo ""
    read -p "Create collection with similar resources? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        COLLECTION_ID=$(pharos collection create "$COLLECTION_NAME" --format quiet)
        echo "Created collection: $COLLECTION_ID"
        
        IDS=$(jq -r '.recommendations[].resource_id' /tmp/similar.json | tr '\n' ',' | sed 's/,$//')
        for id in $IDS; do
            pharos collection add "$COLLECTION_ID" "$id"
        done
        
        echo "Added $TOTAL resources to collection $COLLECTION_ID"
    fi
else
    echo "No similar resources found"
fi

echo ""
echo "=========================================="
echo "Complete"
echo "=========================================="