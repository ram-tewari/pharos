# Pharos CLI Examples

This directory contains example scripts demonstrating how to use Pharos CLI in various scenarios.

## Scripts

### import_project.sh
Import a project directory into Pharos with automatic language detection and collection creation.

**Usage:**
```bash
./import_project.sh <project_directory> [collection_name]
```

**Example:**
```bash
./import_project.sh ./my_project "My Project"
```

### backup_and_cleanup.sh
Create a backup and optionally clean up low-quality resources.

**Usage:**
```bash
./backup_and_cleanup.sh [--keep-backups N]
```

**Example:**
```bash
./backup_and_cleanup.sh --keep-backups 10
```

### generate_report.sh
Generate a comprehensive report of your Pharos knowledge base.

**Usage:**
```bash
./generate_report.sh [output_directory]
```

**Example:**
```bash
./generate_report.sh ./reports/$(date +%Y%m%d)
```

### sync_external.sh
Sync external data sources (GitHub, Git, local directories) to Pharos.

**Usage:**
```bash
./sync_external.sh <source_type> <source_path>
```

**Examples:**
```bash
./sync_external.sh local ./my_project
./sync_external.sh github owner/repo
./sync_external.sh git https://github.com/user/repo.git
```

### find_similar.sh
Find resources similar to a given resource and optionally create a collection.

**Usage:**
```bash
./find_similar.sh <resource_id> [limit]
```

**Example:**
```bash
./find_similar.sh 123
./find_similar.sh 123 20
```

### analyze_codebase.sh
Analyze a codebase and generate a quality report.

**Usage:**
```bash
./analyze_codebase.sh <directory> [--output file.json]
```

**Example:**
```bash
./analyze_codebase.sh ./src --output analysis.json
```

### batch_operations.sh
Perform various batch operations on resources.

**Usage:**
```bash
./batch_operations.sh <operation> [options]
```

**Operations:**
- `delete-low-quality` - Delete resources below quality threshold
- `export-collection` - Export a collection
- `update-tags` - Update tags for matching resources
- `reclassify` - Reclassify resources by type

**Examples:**
```bash
./batch_operations.sh delete-low-quality --threshold 0.5
./batch_operations.sh export-collection 1 --output export.zip
./batch_operations.sh update-tags "*.py" --add-tag python
```

## Using the Scripts

### Make Scripts Executable

```bash
chmod +x *.sh
```

### Run a Script

```bash
./script_name.sh
```

### Customize Configuration

You can customize the scripts by:
1. Editing the script directly
2. Setting environment variables
3. Passing command-line arguments

### Environment Variables

Many scripts respect these environment variables:

```bash
export PHAROS_API_URL="https://pharos.onrender.com"
export PHAROS_API_KEY="your-api-key"
export PHAROS_OUTPUT_FORMAT="json"
export WORKERS=4
```

## Prerequisites

- Pharos CLI installed and configured
- `jq` for JSON processing
- `git` for Git operations (optional)
- `gh` CLI for GitHub operations (optional)

## Installation

```bash
# Install Pharos CLI
pip install pharos-cli

# Install jq
# Ubuntu/Debian:
sudo apt install jq

# macOS:
brew install jq

# Configure Pharos
pharos config init
```

## Next Steps

- Read the [Scripting Guide](../scripting-guide.md) for more details
- Check the [Tutorial: Batch Operations](../tutorial-batch-operations.md)
- See the [Tutorial: CI/CD Integration](../tutorial-ci-cd.md) for CI/CD examples

## Contributing

To add a new example script:

1. Create a new `.sh` file in this directory
2. Add a shebang: `#!/bin/bash`
3. Add usage documentation at the top
4. Implement the script
5. Test the script
6. Add to this README

## License

These example scripts are provided as-is for demonstration purposes.