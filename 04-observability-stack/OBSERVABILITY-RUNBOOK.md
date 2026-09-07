# Observability Stack Runbook

## Stack Overview
| Component | Role |
|-----------|------|
| Prometheus | Metrics collection and alerting engine |
| Grafana | Dashboard visualisation and alert UI |
| AlertManager | Alert routing and notification |
| Node Exporter | Hardware metrics per node (CPU, memory, disk) |
| Kube State Metrics | Kubernetes object state metrics (pod counts, restarts) |

## Deployment
Deployed via Helm on a 3-node kind Kubernetes cluster:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=DevOps2026!
```

## Accessing the Stack

```bash
# Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Open: http://localhost:3000  login: admin / DevOps2026!

# Prometheus
kubectl port-forward -n monitoring \
  svc/monitoring-kube-prometheus-prometheus 9090:9090
# Open: http://localhost:9090
```

## Key PromQL Queries

### CPU Usage Per Node

100 - (avg by (instance)
(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)


### Memory Usage Per Node

(1 - (node_memory_MemAvailable_bytes /
node_memory_MemTotal_bytes)) * 100


### Pod Restart Rate

rate(kube_pod_container_status_restarts_total[15m]) * 900


### Running Pods Per Namespace

count by (namespace) (kube_pod_status_phase{phase="Running"})


## Alert Rules Configured
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| HighCPUUsage | CPU > 70% for 5min | Warning | Check top processes, consider scaling |
| HighMemoryUsage | Memory > 80% for 5min | Critical | Check for memory leaks, restart pod |
| PodCrashLooping | >3 restarts in 15min | Critical | kubectl logs --previous, check OOM |

## Incident Diagnosis Workflow

### Step 1 — Identify the problem
Check the Grafana cluster dashboard for which node or pod
is showing abnormal metrics.

### Step 2 — Confirm with PromQL
Run the relevant query in Prometheus UI to get exact values
and confirm the alert threshold is genuinely breached.

### Step 3 — Cross-reference with kubectl
```bash
# High CPU
kubectl top nodes
kubectl top pods --all-namespaces

# Crash looping
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace> --previous

# Memory pressure
kubectl describe node <node-name>
# Look for: Conditions → MemoryPressure
```

### Step 4 — Apply fix
Based on root cause:
- Resource exhaustion → adjust requests/limits or scale nodes
- Application bug → fix code, redeploy
- Misconfiguration → correct YAML, reapply

### Step 5 — Verify recovery
Confirm the metric returns to normal in Grafana within
one scrape interval (default 30 seconds).

## Dashboard as Code
The Grafana cluster dashboard is exported as JSON in
grafana-dashboard.json — reimport via:
Grafana → Dashboards → Import → Upload JSON file

## What I Learned
- Helm installs complex multi-component stacks in a single command
- PrometheusRule CRDs allow alert rules to be version-controlled
- PromQL is a powerful query language for time-series metrics
- Dashboard-as-code means monitoring configuration is reproducible
- Node Exporter provides hardware-level metrics unavailable from K8s API alone
- kind clusters on resource-constrained machines need memory limits set
  to prevent pod eviction during long sessions
