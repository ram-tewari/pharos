# Authentication Guide

This guide covers all authentication methods for Pharos CLI, including API key authentication, OAuth2, and token management.

## Authentication Overview

Pharos CLI supports two authentication methods:

1. **API Key Authentication** - Simple, suitable for scripts and CI/CD
2. **OAuth2 Authentication** - Interactive, suitable for local development

Both methods store credentials securely using your system's keyring.

## Authentication Requirements

Before authenticating, ensure you have:

- A Pharos account with API access
- Your API credentials (API key or OAuth2 client)
- Network access to your Pharos API endpoint

## Method 1: API Key Authentication

### Getting Your API Key

1. **From the Web Interface:**
   - Log in to your Pharos instance (e.g., https://pharos.onrender.com)
   - Navigate to Settings → API
   - Generate a new API key
   - Copy the key (shown only once)

2. **From the Backend (self-hosted):**
   ```bash
   # If you have admin access
   pharos admin api-key create --user your@email.com
   ```

### Authenticating with API Key

**Interactive prompt:**
```bash
pharos auth login
# Prompts for API key
```

**Command-line option:**
```bash
pharos auth login --api-key YOUR_API_KEY_HERE
```

**Using environment variable:**
```bash
export PHAROS_API_KEY="YOUR_API_KEY_HERE"
pharos resource list
```

### Verifying Authentication

```bash
# Check current user
pharos auth whoami

# Expected output:
# Logged in as: your@email.com
# User ID: 12345
# Plan: premium
# Expires: 2024-12-31
```

## Method 2: OAuth2 Authentication

OAuth2 provides an interactive login flow suitable for local development.

### Initiating OAuth2 Login

```bash
pharos auth login --oauth
```

This will:

1. Open your default browser to the Pharos login page
2. After successful login, redirect to a callback URL
3. Display an authorization code
4. Exchange the code for tokens (automatically)
5. Store tokens securely in keyring

### Manual OAuth2 Flow

If browser opening fails:

```bash
pharos auth login --oauth --no-browser
```

Output:
```
1. Open this URL in your browser:
   https://pharos.onrender.com/oauth/authorize?client_id=...

2. After login, you will be redirected to:
   http://localhost:12345/callback?code=AUTH_CODE

3. Enter the authorization code below:
```

### OAuth2 with Custom Client

For self-hosted instances with custom OAuth2 client:

```bash
pharos auth login --oauth \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --redirect-uri http://localhost:12345/callback
```

## Token Management

### Token Types

| Token Type | Purpose | Lifetime |
|------------|---------|----------|
| Access Token | API requests | 1 hour |
| Refresh Token | Get new access tokens | 30 days |
| API Key | Permanent authentication | Until revoked |

### Automatic Token Refresh

Pharos CLI automatically refreshes expired tokens:

```bash
# Token refresh is automatic
# No action required

# Check token status
pharos auth whoami
```

### Manual Token Refresh

If automatic refresh fails:

```bash
pharos auth refresh
```

### Viewing Token Status

```bash
pharos auth whoami --verbose

# Output:
# Logged in as: your@email.com
# User ID: 12345
# Access Token: Expires in 45 minutes
# Refresh Token: Expires in 29 days
# Token Type: Bearer
```

## Logging Out

### Standard Logout

```bash
pharos auth logout

# Output:
# ✓ Logged out successfully
# ✓ Removed credentials from keyring
# ✓ Cleared session data
```

### Logout from All Devices

```bash
pharos auth logout --all-devices

# Output:
# ✓ Logged out from this device
# ✓ Revoked tokens on server
# ✓ Logged out from 3 other devices
```

### Force Logout (Clear Keyring)

```bash
pharos auth logout --force

# Clears local credentials even if server logout fails
```

## Credential Storage

### Where Credentials Are Stored

| Platform | Storage Location |
|----------|-----------------|
| macOS | Keychain (System Keychain) |
| Windows | Windows Credential Manager |
| Linux | Secret Service (GNOME Keyring) or pass |

### Viewing Stored Credentials

```bash
# Show credential status (masked)
pharos auth status

# Output:
# Status: Authenticated
# User: your@email.com
# Storage: macOS Keychain
# Keyring Entry: pharos-cli/default
```

### Credential Security

- **API Keys:** Stored encrypted in keyring
- **OAuth Tokens:** Stored encrypted in keyring
- **Never logged:** Credentials are never printed or logged
- **Memory only:** Credentials loaded into memory for API calls

### Troubleshooting Keyring

**Keyring not available:**
```bash
# Install keyring with all backends
pip install keyring[all]

# Or use environment variable fallback
export PHAROS_API_KEY="your-key"
```

**Keyring access denied:**
```bash
# Try with explicit backend
export PHAROS_BACKEND=keyring.backends.fail.Keyring
pharos auth login --api-key YOUR_KEY
```

## CI/CD Authentication

For automated pipelines, use API keys with environment variables:

### GitHub Actions

```yaml
# .github/workflows/pharos.yml
name: Pharos Integration

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Pharos CLI
        run: pip install pharos-cli
      
      - name: Authenticate
        run: |
          echo "${{ secrets.PHAROS_API_KEY }}" | pharos auth login --api-key
        env:
          PHAROS_API_KEY: ${{ secrets.PHAROS_API_KEY }}
          PHAROS_API_URL: https://pharos.onrender.com
      
      - name: Run Pharos Commands
        run: |
          pharos resource list
          pharos search "security" --format json
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - analyze

pharos_analysis:
  stage: analyze
  image: python:3.11-slim
  variables:
    PHAROS_API_URL: https://pharos.onrender.com
  before_script:
    - pip install pharos-cli
    - echo "$PHAROS_API_KEY" | pharos auth login --api-key
  script:
    - pharos resource list
    - pharos code scan . --recursive
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    environment {
        PHAROS_API_URL = 'https://pharos.onrender.com'
        PHAROS_API_KEY = credentials('pharos-api-key')
    }
    stages {
        stage('Pharos Analysis') {
            steps {
                sh '''
                    pip install pharos-cli
                    echo "$PHAROS_API_KEY" | pharos auth login --api-key
                    pharos resource list
                '''
            }
        }
    }
}
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

RUN pip install pharos-cli

# Set environment variables at runtime
ENV PHAROS_API_URL=https://pharos.onrender.com
ENV PHAROS_API_KEY=${PHAROS_API_KEY}

CMD ["pharos", "resource", "list"]
```

```bash
# Run with credentials
docker run -e PHAROS_API_KEY="your-key" pharos-cli pharos resource list
```

## Multiple Accounts

### Switching Accounts

```bash
# Log in to different account
pharos auth logout
pharos auth login --api-key DIFFERENT_KEY

# Or use profiles
pharos --profile personal auth login --api-key PERSONAL_KEY
pharos --profile work auth login --api-key WORK_KEY

# Switch between them
pharos --profile personal resource list
pharos --profile work resource list
```

### Managing Multiple Credentials

```bash
# List all stored credentials
pharos auth list-credentials

# Output:
# Profile: default
#   User: user1@example.com
#   Storage: macOS Keyring
# 
# Profile: work
#   User: user2@company.com
#   Storage: macOS Keyring
```

## Troubleshooting Authentication

### "Authentication Failed" Error

**Cause:** Invalid API key or expired token.

**Solutions:**
```bash
# Verify API key
echo $PHAROS_API_KEY

# Re-authenticate
pharos auth logout
pharos auth login --api-key YOUR_KEY

# Check API URL is correct
pharos config show
```

### "Connection Refused" Error

**Cause:** Cannot reach the API server.

**Solutions:**
```bash
# Check API URL
pharos config show

# Test connectivity
curl https://pharos.onrender.com/health

# Check for proxy issues
export HTTP_PROXY=""
export HTTPS_PROXY=""
pharos auth login
```

### "Token Expired" Error

**Cause:** Access token has expired.

**Solutions:**
```bash
# Automatic refresh should handle this
# If not, manually refresh
pharos auth refresh

# If refresh fails, re-authenticate
pharos auth logout
pharos auth login
```

### "Keyring Error"

**Cause:** Keyring backend not available or inaccessible.

**Solutions:**
```bash
# Install keyring with backends
pip install keyring[all]

# Use environment variable fallback
export PHAROS_API_KEY="your-key"
pharos resource list

# Or use file-based storage (less secure)
export PHAROS_KEYRING_BACKEND=keyring.backends.file.PlaintextKeyring
```

### OAuth2 Browser Issues

**Cause:** Browser not opening or callback not working.

**Solutions:**
```bash
# Use manual mode
pharos auth login --oauth --no-browser

# Or use API key instead
pharos auth login --api-key YOUR_KEY
```

## Security Best Practices

1. **Use API keys for CI/CD** - Easier to rotate and audit
2. **Rotate keys regularly** - Generate new keys periodically
3. **Use environment variables** - Never commit keys to code
4. **Limit token lifetime** - Use shorter-lived tokens for sensitive operations
5. **Monitor usage** - Check API logs for unauthorized access
6. **Use HTTPS** - Always verify SSL certificates

## Next Steps

- **[Configuration Guide](configuration.md)** - Configure profiles and settings
- **[Command Reference](commands.md)** - Explore available commands
- **[Examples](examples.md)** - Common workflows

## Getting Help

- **[Troubleshooting](troubleshooting.md)** - Common authentication issues
- **[FAQ](faq.md)** - Frequently asked questions
- **[GitHub Issues](https://github.com/pharos-project/pharos-cli/issues)** - Report problems