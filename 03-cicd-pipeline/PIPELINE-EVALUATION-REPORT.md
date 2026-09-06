# CI/CD Pipeline Evaluation Report

## Pipeline Overview
Four-stage GitHub Actions pipeline for automated Lambda deployment
with built-in quality gates and evaluation reporting.

## Architecture

Push to main
│
├── Stage 1: Validate IaC (23s)
│ ├── Terraform fmt check
│ ├── Terraform init + validate
│ └── Checkov security scan (soft_fail)
│
├── Stage 2: Unit Tests (15s)
│ ├── Python 3.12 setup
│ ├── moto/pytest dependencies
│ └── 4 tests — all passing
│
├── Stage 3: Deploy to AWS (15s)
│ ├── AWS credentials via GitHub Secrets
│ ├── Lambda zip + update-function-code
│ ├── Wait for function-updated
│ └── Smoke test — accepts 200 or 404
│
└── Stage 4: Evaluation Report (5s)
├── Generates structured pass/fail report
└── Uploads as downloadable artifact


## Quality Gates
- Stage 3 blocked unless Stage 1 AND Stage 2 pass
- Smoke test fails pipeline if Lambda returns unexpected status
- Checkov security warnings logged but non-blocking (soft_fail)

## Checkov Security Findings (Informational)
All findings are best-practice recommendations for production
hardening — acceptable for a development/portfolio environment:
- CKV_AWS_119: DynamoDB KMS encryption (uses AWS-managed keys)
- CKV_AWS_28: DynamoDB point-in-time recovery not enabled
- CKV_AWS_117: Lambda not in VPC (not required for this use case)
- CKV_AWS_50: X-Ray tracing not enabled

## Debugging Log
| Run | Stage Failed | Root Cause | Fix Applied |
|-----|-------------|------------|-------------|
| #1  | Unit Tests  | Test path wrong (inside subfolder) | Moved .github/ to repo root |
| #2  | Unit Tests  | pytest path still incorrect | Fixed to 03-cicd-pipeline/tests/ |
| #3  | Deploy      | Lambda did not exist (terraform destroy) | Re-ran terraform apply |
| #4  | Deploy      | Zip had nested path (03-cicd-pipeline/lambda_function.py) | Fixed cd && zip |
| #5  | Deploy      | Smoke test used py (Windows) on Linux runner | Replaced with python3 |
| #6  | None        | All stages passed | Pipeline complete |

## Lessons Learned
1. GitHub Actions .github/workflows/ must be at repo ROOT not in subfolder
2. Zip commands must produce flat structure — Lambda handler must be at root of zip
3. py is Windows-only — always use python3 in GitHub Actions workflows
4. A 404 from your own API is a passing smoke test — proves routing works
5. soft_fail on Checkov allows security visibility without blocking delivery
