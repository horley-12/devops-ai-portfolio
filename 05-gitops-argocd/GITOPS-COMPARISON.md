# GitOps vs Traditional Push-Based Deployment

## What is GitOps?
GitOps is a deployment methodology where Git is the single source
of truth for infrastructure and application state. A GitOps operator
(ArgoCD in this project) continuously reconciles the live cluster
state with the desired state declared in Git.

## Side-by-Side Comparison

| Aspect | Traditional Push-Based | GitOps (ArgoCD) |
|--------|----------------------|-----------------|
| Deployment trigger | Engineer runs kubectl apply | Git push triggers auto-sync |
| Source of truth | Live cluster state | Git repository |
| Rollback method | kubectl rollout undo | git revert + push |
| Audit trail | kubectl history (limited) | Full Git commit history |
| Access required | kubectl access to cluster | Git access only |
| Drift detection | Manual / none | Continuous — ArgoCD alerts on drift |
| Recovery from failure | Manual reapply | ArgoCD auto-heals to Git state |

## How This Project Works

Developer pushes to GitHub
│
▼
ArgoCD polls repo every 3 minutes
│
▼
Detects diff between Git state and cluster state
│
▼
Auto-syncs cluster to match Git (no human intervention)
│
▼
Cluster state = Git state


## Demos Completed

### Demo 1 — Image Version Update
- Changed nginx image from 1.25.0 → 1.26.0 in deployment.yaml
- Pushed to GitHub
- ArgoCD detected change within 3 minutes
- Cluster updated automatically — new pods running 1.26.0
- Zero kubectl commands used for the deployment

### Demo 2 — Git Revert Rollback
- Ran: git revert HEAD && git push origin main
- ArgoCD detected the revert
- Cluster automatically rolled back to nginx:1.25.0
- Rollback completed without touching the cluster directly

## When to Use GitOps vs Traditional Push

### Use GitOps when:
- Multiple engineers deploy to the same cluster
- Audit trail of every deployment is required
- Self-healing and drift correction is needed
- You want rollback to be as simple as git revert

### Use Traditional Push when:
- Single developer, single cluster, rapid iteration
- CI/CD pipeline needs to deploy in under 30 seconds
- Cluster is ephemeral (created and destroyed per test run)
- ArgoCD overhead is not justified for the workload size

## Key ArgoCD Concepts

**Sync:** ArgoCD applying Git state to the cluster
**Self-heal:** ArgoCD correcting manual cluster changes to match Git
**Prune:** ArgoCD removing cluster resources deleted from Git
**Health:** Application pods running and passing health checks
**OutOfSync:** Git state differs from cluster state — sync needed

## What This Proves
Ability to implement production GitOps workflows — the deployment
methodology used by forward-thinking engineering teams in 2026.
