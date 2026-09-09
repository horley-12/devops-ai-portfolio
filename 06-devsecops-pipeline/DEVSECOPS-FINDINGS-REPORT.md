# DevSecOps Security Findings Report

## Pipeline Overview
Three-stage security scanning pipeline integrated into CI/CD.
Scans run on every push to main that touches this project.

## Tools and Coverage

| Tool | Type | What it Catches |
|------|------|----------------|
| pip-audit | Dependency scan | Known CVEs in Python packages (PyPI Advisory DB) |
| Trivy (image) | Container scan | OS-level CVEs, library vulnerabilities in layers |
| Trivy (filesystem) | Source scan | Secrets, misconfigurations, vulnerable dependencies |
| Checkov | IaC scan | Terraform misconfigurations, security best practices |

## Severity Classification

| Severity | Definition | Pipeline Action |
|----------|-----------|----------------|
| CRITICAL | Remote code execution, auth bypass | Would block in production |
| HIGH | Privilege escalation, data exposure | Would block in production |
| MEDIUM | Limited impact vulnerabilities | Logged, non-blocking |
| LOW | Minimal impact | Informational only |

## Finding Categories

### 1. Dependency Vulnerabilities (pip-audit)
Scans requirements.txt against the PyPI Advisory Database.
Common findings in boto3 ecosystem: transitive dependency CVEs
in urllib3, certifi, or requests packages.
Remediation: Pin to patched version in requirements.txt

### 2. Container Image Vulnerabilities (Trivy)
Scans each layer of the Docker image for known CVEs.
python:3.12-slim base image minimises attack surface vs full image.
SARIF results uploaded to GitHub Security tab for tracking.

### 3. IaC Misconfigurations (Checkov)
Common findings in development Terraform:
- CKV_AWS_119: DynamoDB not using KMS CMK (uses AWS-managed keys)
- CKV_AWS_117: Lambda not in VPC (acceptable for public API)
- CKV_AWS_116: No Dead Letter Queue (acceptable for dev)
Accepted risk: These are development environment trade-offs.
Production Terraform would address all HIGH/CRITICAL findings.

## Security Philosophy
DevSecOps means security is part of delivery — not a gate that
blocks it. All scans are non-blocking (exit-code 0) to maintain
deployment velocity while providing full visibility. The SARIF
upload to GitHub Security tab creates a persistent audit trail
of every finding across every run.

## SARIF Integration
Trivy container scan results are uploaded to GitHub Security tab
via SARIF format. This enables:
- Persistent tracking of findings across commits
- Dismissal workflow for accepted risks
- Integration with GitHub dependency review
View results: github.com/horley-12/devops-ai-portfolio/security/code-scanning
