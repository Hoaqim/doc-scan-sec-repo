# DocScanSec: Lightweight CI/CD Container Security

[![Docker Build](https://github.com/hoaqim/doc-scan-sec-repo/actions/workflows/publish-docker.yml/badge.svg)](https://github.com/hoaqim/doc-scan-sec-repo/actions)
[![Security Scan](https://img.shields.io/badge/Security-Syft%20%7C%20Grype-blue)](#)

**DocScanSec** is a blazingly fast, all-in-one CLI tool built for DevOps & Security teams who are tired of bloated container scanners and outdated security documentation.

It wraps **Syft** (for SBOM generation) and **Grype** (for vulnerability scanning) into a single, low-resource Docker container. Most importantly, it **automatically updates your GitHub repository's Markdown documentation** with the latest scan results and suggests base image auto-fixes.

## Why DocScanSec? (The Problem it Solves)
Heavyweight container scanners often slow down CI/CD pipelines, produce massive amounts of false positives, and leave developers manually updating security compliance docs. 
DocScanSec solves this by providing:
- **Performance:** Uses lightweight Syft/Grype binaries optimized for fast CI/CD execution.
- **Low Resource Mode:** Option to scan only the squashed image layer to save CI/CD minutes.
- **Auto-Documentation:** Automatically pushes a `SECURITY_REPORT.md` to your GitHub repo via API. No git-cloning gymnastics required.
- **Smart Auto-Fix:** Analyzes your `Dockerfile` and queries DockerHub API to suggest safer, updated base image tags.

## Quick Start

### Running in GitHub Actions (Recommended)
You don't need to install anything. Just drop this snippet into your workflow:

```yaml
jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: write # Required for auto-updating docs
    steps:
      - name: Run DocScanSec
        run: |
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -e GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }} \
            -e GITHUB_REPOSITORY=${{ github.repository }} \
            ghcr.io/hoaqim/docscansec:main \
            scan my-app:latest --docs-update --auto-fix --severity Critical,High
```
### Running Locally
# Export your GitHub token if you want to use the auto-doc feature
export GITHUB_TOKEN="your_path_here"
export GITHUB_REPOSITORY="your-user/your-repo"

# Run the scan
docscansec scan my-docker-image:latest --auto-fix --docs-update

# Features & Flags
image: Target Docker image (e.g., nginx:alpine).

--low-resource: Optimizes Syft/Grype to scan only the squashed layers instead of full history.

--docs-update: Pushes a clean, markdown-formatted vulnerability summary directly to SECURITY_REPORT.md in your repo.

--auto-fix: Checks your local Dockerfile against DockerHub and suggests upgrading FROM images to their latest stable non-RC tags.

--severity: Filter alerts, can be single or multiple at once (e.g., Low or Critical,High).
