#!/bin/bash
# analyze_codebase.sh - Analyze a codebase and generate report
#
# Usage: ./analyze_codebase.sh <directory> [--output file.json]
#
# This script:
# 1. Scans the codebase
# 2. Analyzes each file
# 3. Checks quality
# 4. Generates a report

set -e

DIRECTORY="${1:-./src}"
OUTPUT_FILE="${2:-./codebase_analysis.json}"

echo "=========================================="
echo "Codebase Analysis"
echo "=========================================="
echo "Directory: $DIRECTORY"
echo "Output: $OUTPUT_FILE"
echo ""

# Check if directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory not found: $DIRECTORY"
    exit 1
fi

# Scan codebase
echo "Scanning codebase..."
pharos code scan "$DIRECTORY" --format json > /tmp/scan_results.json

# Get statistics
echo "Analyzing results..."

# Count files by language
LANGUAGES=$(jq -r '[.files[].language] | unique | .[]' /tmp/scan_results.json | wc -l)
TOTAL_FILES=$(jq '.total_files' /tmp/scan_results.json)

echo "Total files: $TOTAL_FILES"
echo "Languages: $LANGUAGES"

# Quality summary
echo ""
echo "Quality summary:"
pharos quality outliers --min-score 0.5 --format json > /tmp/quality.json
LOW_QUALITY=$(jq '.total' /tmp/quality.json)
echo "Low-quality files: $LOW_QUALITY"

# Generate report
echo ""
echo "Generating report..."

jq -n \
    --arg directory "$DIRECTORY" \
    --argjson total_files "$TOTAL_FILES" \
    --argjson low_quality "$LOW_QUALITY" \
    --argjson timestamp "$(date -Iseconds)" \
    --argfile scan_results /tmp/scan_results.json \
    --argfile quality /tmp/quality.json \
    '{
        directory: $directory,
        timestamp: $timestamp,
        summary: {
            total_files: $total_files,
            low_quality_count: $low_quality,
            quality_percentage: (($total_files - $low_quality) / $total_files * 100 | floor | tostring) + "%"
        },
        scan_results: $scan_results,
        quality_issues: $quality
    }' > "$OUTPUT_FILE"

echo "Report saved to: $OUTPUT_FILE"

# Display summary
echo ""
echo "=========================================="
echo "Analysis Complete"
echo "=========================================="
echo "Total files analyzed: $TOTAL_FILES"
echo "Low-quality files: $LOW_QUALITY"
echo "Quality score: $(($TOTAL_FILES - $LOW_QUALITY))/$TOTAL_FILES ($(($TOTAL_FILES == 0 ? 100 : (($TOTAL_FILES - $LOW_QUALITY) * 100 / $TOTAL_FILES)))%)"
echo ""
echo "Detailed report: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  - Review low-quality files: pharos quality outliers --min-score 0.5"
echo "  - Fix quality issues in your code"
echo "  - Re-run analysis"