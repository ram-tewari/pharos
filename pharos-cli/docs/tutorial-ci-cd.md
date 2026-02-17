# CI/CD Integration Tutorial

Learn how to integrate Pharos CLI into your continuous integration and deployment pipelines.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [Azure DevOps](#azure-devops)
- [CircleCI](#circleci)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Security Best Practices](#security-best-practices)
- [Example Workflows](#example-workflows)

---

## Overview

Integrating Pharos into your CI/CD pipeline enables:

- **Automated code analysis** - Analyze new code automatically
- **Quality gates** - Block low-quality code from merging
- **Knowledge base sync** - Keep your knowledge base updated
- **Reporting** - Generate quality reports on every build
- **Backup automation** - Regular automated backups

### Key Considerations

- Use non-interactive mode for automation
- Store credentials securely (secrets)
- Handle failures gracefully
- Use appropriate output formats for parsing

---

## GitHub Actions

### Basic Workflow

Create `.github/workflows/pharos.yml`:

```yaml
name: Pharos Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  pharos-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure Pharos
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Import Code
        run: |
          pharos resource import ./src/ \
            --pattern "*.py" \
            --type code \
            --workers 4
      
      - name: Run Code Analysis
        run: |
          pharos code scan ./src/ --format json > analysis.json
          echo "Analysis complete"
      
      - name: Check Quality
        run: |
          pharos quality outliers --format json > quality.json
          if [ $(jq '.total' quality.json) -gt 0 ]; then
            echo "Quality issues found:"
            jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
            exit 1
          fi
```

### Quality Gate Workflow

```yaml
name: Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Analyze Changed Files
        run: |
          # Get changed Python files
          CHANGED_FILES=$(git diff --name-only HEAD~1 | grep '\.py$' | tr '\n' ' ')
          
          if [ -n "$CHANGED_FILES" ]; then
            echo "Analyzing: $CHANGED_FILES"
            for file in $CHANGED_FILES; do
              pharos code analyze "$file" --format json
            done
          else
            echo "No Python files changed"
          fi
      
      - name: Quality Gate
        run: |
          pharos quality outliers --min-score 0.5 --format json > quality.json
          
          TOTAL=$(jq '.total' quality.json)
          if [ "$TOTAL" -gt 0 ]; then
            echo "::warning::Found $TOTAL low-quality resources"
            jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
            # Exit with error for quality gate
            # exit 1
          fi
```

### Scheduled Backup Workflow

```yaml
name: Daily Backup

on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          sparse-checkout: |
            backups
          sparse-checkout-cone-mode: false
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Create Backup
        run: |
          DATE=$(date +%Y%m%d)
          pharos backup --output "backups/backup_$DATE.json"
      
      - name: Upload Backup
        uses: actions/upload-artifact@v4
        with:
          name: pharos-backup
          path: backups/
          retention-days: 30
```

### Matrix Build for Multiple Languages

```yaml
name: Multi-Language Analysis

on:
  push:
    paths:
      - '**.py'
      - '**.js'
      - '**.ts'
      - '**.java'

jobs:
  analyze:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [python, javascript, typescript, java]
        exclude:
          - language: python
            path: '**.py'
          - language: javascript
            path: '**.js'
          - language: typescript
            path: '**.ts'
          - language: java
            path: '**.java'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Import Code
        run: |
          pharos resource import ./src/ \
            --pattern "*.${{ matrix.language }}" \
            --type code \
            --language ${{ matrix.language }}
      
      - name: Analyze
        run: |
          pharos code scan ./src/ --format json > analysis_${{ matrix.language }}.json
```

---

## GitLab CI

### Basic Configuration

Create `.gitlab-ci.yml`:

```yaml
stages:
  - analyze
  - quality
  - backup

variables:
  PHAROS_URL: $PHAROS_URL
  PHAROS_API_KEY: $PHAROS_API_KEY

.pharos-setup:
  before_script:
    - pip install pharos-cli
    - pharos config init --non-interactive \
        --url $PHAROS_URL \
        --api-key $PHAROS_API_KEY

analyze:
  stage: analyze
  image: python:3.11
  extends: .pharos-setup
  script:
    - pharos resource import ./src/ --pattern "*.py" --type code
    - pharos code scan ./src/ --format json > analysis.json
  artifacts:
    reports:
      json: analysis.json

quality-check:
  stage: quality
  image: python:3.11
  extends: .pharos-setup
  script:
    - pharos quality outliers --min-score 0.5 --format json > quality.json
    - |
      if [ $(jq '.total' quality.json) -gt 0 ]; then
        echo "Quality issues found:"
        jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
        exit 1
      fi
  allow_failure: false

backup:
  stage: backup
  image: python:3.11
  extends: .pharos-setup
  script:
    - pharos backup --output "backup_$(date +%Y%m%d).json"
  artifacts:
    paths:
      - backup_*.json
    expire_in: 7 days
```

### Scheduled Pipeline

```yaml
# Scheduled backup pipeline
backup_schedule:
  stage: backup
  image: python:3.11
  only:
    - schedules
  before_script:
    - pip install pharos-cli
    - pharos config init --non-interactive \
        --url $PHAROS_URL \
        --api-key $PHAROS_API_KEY
  script:
    - pharos backup --output "backup_$(date +%Y%m%d_%H%M%S).json"
  artifacts:
    paths:
      - backup_*.json
    expire_in: 30 days
```

---

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        PHAROS_URL = credentials('pharos-url')
        PHAROS_API_KEY = credentials('pharos-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install pharos-cli
                    pharos config init --non-interactive \
                        --url $PHAROS_URL \
                        --api-key $PHAROS_API_KEY
                '''
            }
        }
        
        stage('Import Code') {
            steps {
                sh '''
                    pharos resource import ./src/ \
                        --pattern "*.py" \
                        --type code \
                        --workers 4
                '''
            }
        }
        
        stage('Analyze') {
            steps {
                sh '''
                    pharos code scan ./src/ --format json > analysis.json
                '''
                archiveArtifacts artifacts: 'analysis.json', fingerprint: true
            }
        }
        
        stage('Quality Check') {
            steps {
                sh '''
                    pharos quality outliers --min-score 0.5 --format json > quality.json
                    
                    TOTAL=$(jq '.total' quality.json)
                    if [ "$TOTAL" -gt 0 ]; then
                        echo "Quality issues found:"
                        jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
                        currentBuild.result = 'FAILURE'
                    fi
                '''
            }
        }
        
        stage('Backup') {
            steps {
                sh '''
                    DATE=$(date +%Y%m%d)
                    pharos backup --output "backup_$DATE.json"
                '''
                archiveArtifacts artifacts: 'backup_*.json', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo "Pipeline completed"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
```

### Scripted Pipeline

```groovy
node {
    withCredentials([string(credentialsId: 'pharos-api-key', variable: 'PHAROS_API_KEY')]) {
        stage('Install') {
            sh 'pip install pharos-cli'
        }
        
        stage('Configure') {
            sh '''
                pharos config init --non-interactive \
                    --url https://pharos.onrender.com \
                    --api-key $PHAROS_API_KEY
            '''
        }
        
        stage('Import') {
            sh 'pharos resource import ./src/ --pattern "*.py" --type code'
        }
        
        stage('Analyze') {
            sh 'pharos code scan ./src/ --format json > analysis.json'
        }
    }
}
```

---

## Azure DevOps

### YAML Pipeline

```yaml
trigger:
  - main
  - develop

variables:
  - group: pharos-secrets
  - name: pythonVersion
    value: '3.11'

stages:
  - stage: Analyze
    jobs:
      - job: PharosAnalysis
        pool:
          vmImage: 'ubuntu-latest'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
          
          - script: |
              pip install pharos-cli
              pharos config init --non-interactive \
                --url $(PHAROS_URL) \
                --api-key $(PHAROS_API_KEY)
            displayName: 'Install and Configure Pharos'
          
          - script: |
              pharos resource import ./src/ --pattern "*.py" --type code
              pharos code scan ./src/ --format json > $(Build.ArtifactStagingDirectory)/analysis.json
            displayName: 'Import and Analyze Code'
          
          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '$(Build.ArtifactStagingDirectory)/analysis.json'
              artifactName: 'analysis'
          
          - script: |
              pharos quality outliers --min-score 0.5 --format json > $(Build.ArtifactStagingDirectory)/quality.json
              
              TOTAL=$(jq '.total' $(Build.ArtifactStagingDirectory)/quality.json)
              if [ "$TOTAL" -gt 0 ]; then
                echo "##vso[task.logissue type=error]Found $TOTAL low-quality resources"
                exit 1
              fi
            displayName: 'Quality Gate'
```

### Release Pipeline

```yaml
stages:
  - stage: Backup
    jobs:
      - deployment: CreateBackup
        environment: production
        strategy:
          runOnce:
            deploy:
              steps:
                - task: UsePythonVersion@0
                  inputs:
                    versionSpec: '3.11'
                
                - script: |
                    pip install pharos-cli
                    pharos config init --non-interactive \
                      --url $(PHAROS_URL) \
                      --api-key $(PHAROS_API_KEY)
                    pharos backup --output $(Build.ArtifactStagingDirectory)/backup_$(Date:YYYYMMDD).json
                  displayName: 'Create Backup'
                
                - task: PublishBuildArtifacts@1
                  inputs:
                    pathToPublish: '$(Build.ArtifactStagingDirectory)/backup_*.json'
                    artifactName: 'backup'
```

---

## CircleCI

### Config.yml

```yaml
version: 2.1

orbs:
  python: circleci/python@2.0

jobs:
  pharos-analysis:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      
      - python/install-packages:
          pkg-manager: pip
      
      - run:
          name: Configure Pharos
          command: |
            pharos config init --non-interactive \
              --url ${PHAROS_URL} \
              --api-key ${PHAROS_API_KEY}
      
      - run:
          name: Import Code
          command: |
            pharos resource import ./src/ \
              --pattern "*.py" \
              --type code \
              --workers 4
      
      - run:
          name: Analyze
          command: |
            pharos code scan ./src/ --format json > analysis.json
      
      - run:
          name: Quality Check
          command: |
            pharos quality outliers --min-score 0.5 --format json > quality.json
            
            TOTAL=$(jq '.total' quality.json)
            if [ "$TOTAL" -gt 0 ]; then
              echo "Quality issues found:"
              jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
              exit 1
            fi
      
      - store_artifacts:
          path: analysis.json
      
      - store_artifacts:
          path: quality.json

workflows:
  version: 2
  pharos_workflow:
    jobs:
      - pharos-analysis
```

---

## Pre-commit Hooks

### Git Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook for Pharos analysis

# Only run on staged Python files
CHANGED_PY_FILES=$(git diff --cached --name-only | grep '\.py$' || true)

if [ -z "$CHANGED_PY_FILES" ]; then
    echo "No Python files staged, skipping Pharos analysis"
    exit 0
fi

echo "Running Pharos analysis on staged files..."

# Install pharos-cli if not available
if ! command -v pharos &> /dev/null; then
    pip install pharos-cli -q
fi

# Configure if not already configured
if ! pharos config show &> /dev/null; then
    echo "Pharos not configured, skipping analysis"
    exit 0
fi

# Analyze each changed file
for file in $CHANGED_PY_FILES; do
    echo "Analyzing: $file"
    
    # Add file to knowledge base
    RESOURCE_ID=$(pharos resource add "$file" --format quiet 2>/dev/null || echo "")
    
    if [ -n "$RESOURCE_ID" ]; then
        # Check quality
        QUALITY=$(pharos quality score "$RESOURCE_ID" --format json 2>/dev/null | \
                  jq -r '.overall_score' || echo "0")
        
        if (( $(echo "$QUALITY < 0.5" | bc -l) )); then
            echo "Warning: Low quality score ($QUALITY) for $file"
            echo "Consider improving code quality before committing"
        fi
    fi
done

echo "Pharos analysis complete"
exit 0
```

### Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pharos-analysis
        name: Pharos Code Analysis
        entry: bash scripts/pharos_precommit.sh
        language: system
        stages: [pre-commit]
        pass_filenames: false
```

### Python Pre-commit Script

Create `scripts/pharos_precommit.sh`:

```bash
#!/bin/bash
# pharos_precommit.sh - Pre-commit analysis with Pharos

set -e

# Get changed files
CHANGED_FILES=$(git diff --cached --name-only)

# Filter for code files
PYTHON_FILES=$(echo "$CHANGED_FILES" | grep '\.py$' || true)
JS_FILES=$(echo "$CHANGED_FILES" | grep '\.js$' || true)

# Check if Pharos is available
if ! command -v pharos &> /dev/null; then
    echo "Pharos CLI not found, skipping analysis"
    exit 0
fi

# Check if Pharos is configured
if ! pharos config show &> /dev/null; then
    echo "Pharos not configured, skipping analysis"
    exit 0
fi

# Analyze Python files
if [ -n "$PYTHON_FILES" ]; then
    echo "Analyzing Python files..."
    for file in $PYTHON_FILES; do
        echo "  Analyzing: $file"
        pharos code analyze "$file" --format json > /dev/null 2>&1 || true
    done
fi

# Analyze JavaScript files
if [ -n "$JS_FILES" ]; then
    echo "Analyzing JavaScript files..."
    for file in $JS_FILES; do
        echo "  Analyzing: $file"
        pharos code analyze "$file" --format json > /dev/null 2>&1 || true
    done
fi

echo "Pharos analysis complete"
```

---

## Security Best Practices

### 1. Use Secrets for Credentials

```yaml
# GitHub Actions
env:
  PHAROS_API_KEY: ${{ secrets.PHAROS_API_KEY }}
```

### 2. Never Log Credentials

```bash
# BAD - credentials in logs
echo "API Key: $PHAROS_API_KEY"

# GOOD - no credentials logged
pharos config init --non-interactive --url "$PHAROS_URL" --api-key "[REDACTED]"
```

### 3. Use Short-Lived Tokens

```bash
# Rotate API keys regularly
# Use environment-specific keys
```

### 4. Limit Permissions

```yaml
# Use minimal required permissions
permissions:
  contents: read
  actions: read
```

### 5. Verify SSL

```bash
# Always verify SSL in production
pharos config init --verify-ssl
```

### 6. Use Private Repositories

Store credentials in encrypted secrets, never in code.

---

## Example Workflows

### Workflow 1: Complete CI/CD Pipeline

```yaml
name: Complete Pharos Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly backup

jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Verify Connection
        run: pharos health

  import:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Import Code
        run: |
          pharos resource import ./src/ \
            --pattern "*.py" \
            --type code \
            --recursive \
            --workers 4

  analyze:
    needs: import
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Configure
        run: |
          pharos config init --non-interactive \
            --url ${{ secrets.PHAROS_URL }} \
            --api-key ${{ secrets.PHAROS_API_KEY }}
      
      - name: Code Analysis
        run: pharos code scan ./src/ --format json > analysis.json
      
      - name: Quality Check
        run: |
          pharos quality outliers --min-score 0.5 --format json > quality.json
          
          if [ $(jq '.total' quality.json) -gt 0 ]; then
            echo "Quality issues found:"
            jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' quality.json
            exit 1
          fi
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: analysis-results
          path: |
            analysis.json
            quality.json

  backup:
    needs: analyze
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - name: Create Backup
        run: |
          DATE=$(date +%Y%m%d)
          pharos backup --output "backup_$DATE.json"
      
      - name: Upload Backup
        uses: actions/upload-artifact@v4
        with:
          name: pharos-backup
          path: backup_*.json
          retention-days: 30
```

### Workflow 2: Multi-Environment Deployment

```yaml
name: Multi-Environment Pipeline

on:
  push:
    branches: [develop, main]

jobs:
  develop:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: develop
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        run: |
          pip install pharos-cli
          pharos config init --non-interactive \
            --url ${{ secrets.DEV_PHAROS_URL }} \
            --api-key ${{ secrets.DEV_PHAROS_API_KEY }}
      
      - name: Import to Dev
        run: |
          pharos resource import ./src/ --pattern "*.py" --type code
          pharos code scan ./src/ --format json > dev_analysis.json
      
      - name: Quality Check
        run: |
          pharos quality outliers --min-score 0.3 --format json > dev_quality.json
          # Lower threshold for dev

  production:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        run: |
          pip install pharos-cli
          pharos config init --non-interactive \
            --url ${{ secrets.PROD_PHAROS_URL }} \
            --api-key ${{ secrets.PROD_PHAROS_API_KEY }}
      
      - name: Import to Prod
        run: |
          pharos resource import ./src/ --pattern "*.py" --type code
          pharos code scan ./src/ --format json > prod_analysis.json
      
      - name: Quality Gate
        run: |
          pharos quality outliers --min-score 0.7 --format json > prod_quality.json
          # Higher threshold for production
          
          if [ $(jq '.total' prod_quality.json) -gt 0 ]; then
            echo "Quality issues found for production:"
            jq '.outliers[] | "\(.resource_id): \(.quality_overall)"' prod_quality.json
            exit 1
          fi
```

---

## Troubleshooting

### Authentication Failures

```yaml
# Check secrets are configured
- name: Verify Secrets
  run: |
    if [ -z "${{ secrets.PHAROS_API_KEY }}" ]; then
      echo "::error::PHAROS_API_KEY secret not configured"
      exit 1
    fi
```

### Network Timeouts

```bash
# Increase timeout in config
pharos config init --timeout 60
```

### Rate Limiting

```bash
# Use fewer workers to avoid rate limits
pharos resource import ./project/ --workers 2
```

### Permission Denied (Hooks)

```bash
# Make hook executable
chmod +x .git/hooks/pre-commit
```

---

## See Also

- [Command Reference](command-reference.md)
- [Usage Patterns](usage-patterns.md)
- [Workflows](workflows.md)
- [Cheat Sheet](cheat-sheet.md)
- [Scripting Guide](scripting-guide.md)