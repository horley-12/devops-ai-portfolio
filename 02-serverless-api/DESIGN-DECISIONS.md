# Serverless API — Design Decisions

## Architecture Overview
REST API built with AWS Lambda + API Gateway + DynamoDB,
provisioned entirely via Terraform IaC. Zero server management.

## Decision 1: Lambda over ECS for compute
**Chose:** AWS Lambda
**Reason:** Workload is stateless request/response with unpredictable
traffic — Lambda scales to zero when idle (zero cost) and scales
instantly under load. ECS minimum cost is ~$15/month even with
zero traffic.
**Trade-off:** Cold start latency (~200-500ms) acceptable for this
use case. Would reconsider for latency-sensitive production APIs.

## Decision 2: DynamoDB over RDS for storage
**Chose:** DynamoDB with PAY_PER_REQUEST billing
**Reason:** Single-entity lookups by playerId only — no joins, no
complex queries. DynamoDB GetItem at ~1ms latency vs RDS connection
overhead. Free tier covers 25GB storage and 200M requests/month.
**Trade-off:** Cannot do complex queries or aggregations. Acceptable
for this use case.

## Decision 3: Hash key design
**Chose:** playerId as partition key (String type)
**Reason:** High cardinality — each player has a unique ID ensuring
even data distribution across DynamoDB partitions. UUID-based IDs
prevent hot partition issues that sequential integers would cause.
**Trade-off:** Cannot query by name or team without a GSI.

## Decision 4: PAY_PER_REQUEST over PROVISIONED billing
**Chose:** PAY_PER_REQUEST
**Reason:** Traffic pattern is unpredictable and bursty. Provisioned
capacity requires pre-estimating read/write units — wasteful for
development and variable workloads.
**Trade-off:** Slightly higher per-request cost at very high scale.
Would switch to provisioned with auto-scaling above 1M requests/day.

## Decision 5: Least-privilege IAM policy
**Chose:** Custom policy with only dynamodb:GetItem and dynamodb:PutItem
**Reason:** Lambda only needs to read and write individual items.
Granting AmazonDynamoDBFullAccess would allow DeleteTable, Scan, and
other destructive operations the function should never perform.
**Principle:** Grant only the minimum permissions required. Any
compromise of the Lambda cannot destroy the table.

## Decision 6: Terraform over AWS Console
**Chose:** Terraform IaC for all infrastructure
**Reason:** Reproducible — anyone can clone the repo and run
terraform apply to get an identical environment. Reviewable —
infrastructure changes go through git diff before deployment.
Destroyable — terraform destroy removes all resources cleanly with
no orphaned resources.

## Verified Test Results
- POST /players → 201 Created — player stored in DynamoDB
- GET  /players/:id → 200 OK — player retrieved from DynamoDB  
- GET  /players/ghost → 404 Not Found — missing player handled correctly
