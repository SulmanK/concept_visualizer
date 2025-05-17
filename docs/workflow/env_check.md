# Environment Security Check Workflow

## Overview

The `Environment Security Check` workflow is a security-focused workflow that scans the codebase for hardcoded secrets and validates that environment files follow security best practices. This workflow helps prevent accidental leakage of sensitive information.

## Triggers

This workflow runs when:

- Code is pushed to the `main` branch
- Pull requests are opened against the `main` branch
- Weekly on Sunday at 2:00 AM UTC (scheduled run)
- Manually triggered via GitHub Actions interface (workflow_dispatch)

## Workflow Structure

### Scan for Hardcoded Secrets

**Job name**: `scan-secrets`

This job utilizes GitLeaks to detect potential secrets in the codebase:

1. Checks out the repository with full history
2. Installs GitLeaks from GitHub releases
3. Creates a custom `.gitleaksignore` file to exclude certain files and directories (design files, terminal logs, etc.)
4. Configures GitLeaks with a custom configuration to avoid false positives
5. Runs GitLeaks in detect mode and generates a JSON report
6. Checks if any secrets were found and issues a warning if needed
7. Uploads the scan results as a workflow artifact for review

The GitLeaks configuration excludes:

- `node_modules`
- `package-lock.json`
- `.gitleaksignore`
- `.git/` directory

### Check Environment Files

**Job name**: `check-env-examples`

This job ensures that environment example files follow best practices:

1. Verifies that `.env.example` files exist in both backend and frontend directories
2. Scans these example files for patterns that might indicate real credentials (rather than placeholders)
3. Fails the workflow if actual secrets are detected in example files

The job scans for several credential patterns including:

- Stripe-like keys (`sk_...`)
- API keys
- Passwords
- AWS access keys
- Secret access keys

## Artifacts

The workflow generates a GitLeaks report as an artifact, which is available for download and review after the workflow runs. This helps identify any potential secrets that need to be removed from the codebase.

## Security Benefits

This workflow provides several security benefits:

1. **Secret Detection**: Automated detection of secrets accidentally committed to the repository
2. **Regular Monitoring**: Weekly checks ensure ongoing compliance
3. **Example File Validation**: Ensures example files contain only placeholders, not real credentials
4. **Documentation**: Provides comprehensive reports of potential security issues

## Customization

The workflow can be customized by:

1. Modifying the `.gitleaksignore` file to exclude additional directories
2. Adjusting the GitLeaks configuration to add more rules or exceptions
3. Adding additional credential patterns to check for in example files
4. Changing the schedule for automated runs
