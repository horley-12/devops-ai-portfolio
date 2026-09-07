# Observability Stack Runbook

## Stack Overview
- **Prometheus** — metrics collection and alerting engine
- **Grafana** — dashboard visualisation and alert UI
- **AlertManager** — alert routing and notification
- **Node Exporter** — hardware metrics per node
- **Kube State Metrics** — Kubernetes object state metrics

## Deployment
Stack deployed via Helm on a 3-node kind Kubernetes cluster:
```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=DevOps2026!
```

## Access
```bash
# Grafana dashboard
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Open: http://localhost:3000 (admin / DevOps2026!)

# Prometheus UI
kubectl port-forward -n monitoring \
  svc/monitoring-kube-prometheus-prometheus 9090:9090
# Open: http://localhost:9090
```

## Key PromQL Queries

### CPU Usage Per Node
```promql
100 - (avg by (instance)
  (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

### Memory Usage Per Node
```promql
(1 - (node_memory_MemAvailable_bytes /
  node_memory_MemTotal_bytes)) * 100
```

### Pod Restart Rate
```promql
rate(kube_pod_container_status_restarts_total[15m]) * 900
```

### Running Pods Per Namespace
```promql
count by (namespace) (kube_pod_status_phase{phase="Running"})
```

## Alert Rules Configured
| Alert | Condition | Severity |
|-------|-----------|----------|
| HighCPUUsage | CPU > 70% for 5min | Warning |
| HighMemoryUsage | Memory > 80% for 5min | Critical |
| PodCrashLooping | >3 restarts in 15min | Critical |

## Incident Diagnosis Workflow
1. Check Grafana cluster dashboard — identify which node/pod
2. Run PromQL query to confirm the metric value
3. Cross-reference with kubectl:
   - High CPU → kubectl top nodes / kubectl top pods
   - Crash looping → kubectl describe pod / kubectl logs --previous
   - Memory pressure → kubectl describe node (check Conditions)
4. Apply fix based on root cause
5. Verify metric returns to normal in Grafana within 5 minutes

## Dashboard as Code
The Grafana cluster dashboard is exported as JSON in
grafana-dashboard.json — import via:
Grafana → Dashboards → Import → Upload JSON file
