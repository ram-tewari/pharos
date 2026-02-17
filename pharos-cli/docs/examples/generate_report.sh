#!/bin/bash
# generate_report.sh - Generate comprehensive Pharos report
#
# Usage: ./generate_report.sh [output_directory]
#
# This script generates a comprehensive report including:
# - System statistics
# - Resource summary
# - Quality report
# - Collection summaries
# - Graph statistics

set -e

OUTPUT_DIR="${1:-./reports/$(date +%Y%m%d_%H%M%S)}"

echo "=========================================="
echo "Pharos Report Generator"
echo "=========================================="
echo "Output Directory: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# System statistics
echo "Generating system statistics..."
pharos stats --format json > "$OUTPUT_DIR/system_stats.json"

# Resource summary
echo "Generating resource summary..."
pharos resource list --format json > "$OUTPUT_DIR/resources.json"

# Collection list
echo "Generating collection list..."
pharos collection list --format json > "$OUTPUT_DIR/collections.json"

# Quality report
echo "Generating quality report..."
pharos quality outliers --format json > "$OUTPUT_DIR/quality_outliers.json"
pharos quality distribution --format json > "$OUTPUT_DIR/quality_distribution.json"

# Graph statistics
echo "Generating graph statistics..."
pharos graph stats --format json > "$OUTPUT_DIR/graph_stats.json"
pharos graph centrality --top 20 --format json > "$OUTPUT_DIR/centrality.json"

# Taxonomy statistics
echo "Generating taxonomy statistics..."
pharos taxonomy stats --format json > "$OUTPUT_DIR/taxonomy_stats.json"

# Collection-specific reports
echo ""
echo "Generating collection reports..."
for id in $(pharos collection list --format quiet); do
    NAME=$(pharos collection show "$id" --format json | jq -r '.name' | tr ' ' '_' | tr '[:upper:]' '[:lower:]')
    pharos quality report "$id" --format json > "$OUTPUT_DIR/collection_${id}_${NAME}_quality.json"
done

# Generate summary markdown
echo ""
echo "Generating summary..."
cat > "$OUTPUT_DIR/summary.md" << EOF
# Pharos Report - $(date)

## System Statistics
- Total Resources: $(jq '.total' "$OUTPUT_DIR/resources.json")
- Total Collections: $(jq '.total' "$OUTPUT_DIR/collections.json")

## Quality Summary
- Low-quality resources: $(jq '.total' "$OUTPUT_DIR/quality_outliers.json")

## Graph Statistics
- Total entities: $(jq '.total_entities' "$OUTPUT_DIR/graph_stats.json")
- Total relationships: $(jq '.total_relationships' "$OUTPUT_DIR/graph_stats.json")

## Top Centrality
$(jq -r '.[] | "- \(.entity): \(.centrality)"' "$OUTPUT_DIR/centrality.json" | head -10)

## Collections
$(jq -r '.items[] | "- \(.name) (\(.resource_count) resources)"' "$OUTPUT_DIR/collections.json")

---
Generated at $(date)
EOF

echo ""
echo "=========================================="
echo "Report Complete"
echo "=========================================="
echo "Output Directory: $OUTPUT_DIR"
echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"

echo ""
echo "Quick summary:"
echo "  - Resources: $(jq '.total' "$OUTPUT_DIR/resources.json")"
echo "  - Collections: $(jq '.total' "$OUTPUT_DIR/collections.json")"
echo "  - Low-quality: $(jq '.total' "$OUTPUT_DIR/quality_outliers.json")"
echo "  - Graph entities: $(jq '.total_entities' "$OUTPUT_DIR/graph_stats.json")"