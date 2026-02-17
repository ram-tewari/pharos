#!/bin/bash
# batch_operations.sh - Perform batch operations on resources
#
# Usage: ./batch_operations.sh <operation> [options]
#
# Operations:
#   delete-low-quality  - Delete resources with quality below threshold
#   export-collection   - Export a collection to file
#   update-tags         - Update tags for resources matching a pattern
#   reclassify          - Reclassify resources by type
#
# Examples:
#   ./batch_operations.sh delete-low-quality --threshold 0.5
#   ./batch_operations.sh export-collection 1 --output export.zip
#   ./batch_operations.sh update-tags "*.py" --add-tag python

set -e

OPERATION="$1"
shift

if [ -z "$OPERATION" ]; then
    echo "Usage: $0 <operation> [options]"
    echo ""
    echo "Operations:"
    echo "  delete-low-quality  - Delete resources with quality below threshold"
    echo "  export-collection   - Export a collection to file"
    echo "  update-tags         - Update tags for resources"
    echo "  reclassify          - Reclassify resources by type"
    exit 1
fi

case "$OPERATION" in
    delete-low-quality)
        THRESHOLD="${1:-0.5}"
        echo "=========================================="
        echo "Delete Low-Quality Resources"
        echo "=========================================="
        echo "Threshold: $THRESHOLD"
        echo ""
        
        # Get low-quality resources
        pharos quality outliers --min-score "$THRESHOLD" --format json > /tmp/low_quality.json
        TOTAL=$(jq '.total' /tmp/low_quality.json)
        
        if [ "$TOTAL" -eq 0 ]; then
            echo "No low-quality resources found"
            exit 0
        fi
        
        echo "Found $TOTAL low-quality resources:"
        jq -r '.outliers[] | "  [\(.resource_id)] \(.quality_overall // 0)"' /tmp/low_quality.json | head -20
        [ "$TOTAL" -gt 20 ] && echo "  ... and $((TOTAL - 20)) more"
        
        echo ""
        read -p "Delete all $TOTAL resources? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            IDS=$(jq -r '.outliers[].resource_id' /tmp/low_quality.json | tr '\n' ',' | sed 's/,$//')
            pharos batch delete "$IDS" --force
            echo "Deleted $TOTAL resources"
        else
            echo "Cancelled"
        fi
        ;;
        
    export-collection)
        COLLECTION_ID="$1"
        OUTPUT="${2:-collection_${COLLECTION_ID}.zip}"
        FORMAT="${3:-zip}"
        
        if [ -z "$COLLECTION_ID" ]; then
            echo "Usage: $0 export-collection <collection_id> [output] [format]"
            echo ""
            echo "Formats: zip, json, markdown"
            exit 1
        fi
        
        echo "=========================================="
        echo "Export Collection"
        echo "=========================================="
        echo "Collection ID: $COLLECTION_ID"
        echo "Output: $OUTPUT"
        echo "Format: $FORMAT"
        echo ""
        
        pharos collection export "$COLLECTION_ID" --format "$FORMAT" --output "$OUTPUT"
        
        echo "Exported to: $OUTPUT"
        ;;
        
    update-tags)
        PATTERN="$1"
        shift
        
        if [ -z "$PATTERN" ]; then
            echo "Usage: $0 update-tags <pattern> [--add-tag TAG] [--remove-tag TAG]"
            exit 1
        fi
        
        ADD_TAG=""
        REMOVE_TAG=""
        
        while [[ $# -gt 0 ]]; do
            case "$1" in
                --add-tag)
                    ADD_TAG="$2"
                    shift 2
                    ;;
                --remove-tag)
                    REMOVE_TAG="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        echo "=========================================="
        echo "Update Tags"
        echo "=========================================="
        echo "Pattern: $PATTERN"
        echo "Add tag: ${ADD_TAG:-none}"
        echo "Remove tag: ${REMOVE_TAG:-none}"
        echo ""
        
        # Find matching resources
        pharos resource list --format json > /tmp/all_resources.json
        MATCHING_IDS=$(jq -r --arg pattern "$PATTERN" \
            '.items[] | select(.title | test($pattern; "i")) | .id' \
            /tmp/all_resources.json | tr '\n' ',' | sed 's/,$//')
        
        if [ -z "$MATCHING_IDS" ]; then
            echo "No matching resources found"
            exit 0
        fi
        
        COUNT=$(echo "$MATCHING_IDS" | tr ',' '\n' | wc -l)
        echo "Found $COUNT matching resources"
        
        # Create update file
        cat > /tmp/updates.json << UPDATES
{
  "updates": [
$(echo "$MATCHING_IDS" | tr ',' '\n' | while read id; do
    JSON="    {\"id\": $id"
    [ -n "$ADD_TAG" ] && JSON="$JSON, \"tags\": [\"$ADD_TAG\"]"
    [ -n "$REMOVE_TAG" ] && JSON="$JSON, \"tags_to_remove\": [\"$REMOVE_TAG\"]"
    echo "$JSON},"
done | sed '$ s/,$//')
  ]
}
UPDATES
        
        echo ""
        read -p "Apply updates? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pharos batch update /tmp/updates.json --dry-run
            echo ""
            read -p "Apply for real? (y/n) " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                pharos batch update /tmp/updates.json
                echo "Updated $COUNT resources"
            fi
        fi
        ;;
        
    reclassify)
        TYPE="$1"
        
        if [ -z "$TYPE" ]; then
            echo "Usage: $0 reclassify <type>"
            echo ""
            echo "Types: code, paper, documentation, other"
            exit 1
        fi
        
        echo "=========================================="
        echo "Reclassify Resources"
        echo "=========================================="
        echo "Type: $TYPE"
        echo ""
        
        # Get all resources
        pharos resource list --format json > /tmp/all_resources.json
        
        # Create update file for resources without type
        cat > /tmp/updates.json << UPDATES
{
  "updates": [
$(jq -r --arg type "$TYPE" \
    '.items[] | select(.type == null or .type == "") | "    {\"id\": \(.id), \"type\": \"\(type)\"}"' \
    /tmp/all_resources.json | head -100 | sed '$ s/,$//')
  ]
}
UPDATES
        
        COUNT=$(jq '[.updates[] | .id] | length' /tmp/updates.json)
        echo "Found $COUNT resources to reclassify"
        
        if [ "$COUNT" -gt 0 ]; then
            read -p "Apply updates? (y/n) " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                pharos batch update /tmp/updates.json
                echo "Reclassified $COUNT resources"
            fi
        fi
        ;;
        
    *)
        echo "Unknown operation: $OPERATION"
        exit 1
        ;;
esac

echo ""
echo "Complete"