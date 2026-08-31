# Kubernetes Cluster Failure Diagnosis Report

## Lab Environment
- Tool: kind v0.26.0
- Kubernetes: v1.33.0
- Nodes: 1 control-plane + 2 workers
- OS: Windows 11 / Git Bash

## Scenario 1: CrashLoopBackOff
**Signal:** Pod status CrashLoopBackOff
**Root cause:** Container command override exits with code 1
**Diagnostic commands:**
- kubectl describe pod → Events: Back-off restarting failed container
- kubectl logs --previous → output: "starting" then exit
- kubectl describe pod | grep "Exit Code" → Exit Code: 1
**Fix:** Remove bad command override from deployment spec
**Severity:** Low — single deployment, clear root cause, no data loss
**Production equivalent:** Check application entrypoint and startup script

## Scenario 2: ImagePullBackOff
**Signal:** Pod status ErrImagePull → ImagePullBackOff
**Root cause:** Image tag does not exist in registry
**Diagnostic commands:**
- kubectl describe pod → Events: 404 Not Found from registry
- kubectl get events --field-selector reason=Failed
**Fix:** Update deployment to valid image tag
**Severity:** Low-Medium — no running pods, fast fix if correct tag is known
**Production equivalent:** Check registry for valid tags, verify pull secrets

## Scenario 3: Node NotReady
**Signal:** Node STATUS: NotReady after kubelet stops heartbeating
**Root cause:** kubelet process stopped (simulated via docker pause)
**Diagnostic commands:**
- kubectl describe node → Conditions: all Unknown
- kubectl get events --all-namespaces → NodeNotReady events
**Fix:** Restore kubelet process
**Severity:** High — pods evicted after 5min, StatefulSets risk data loss
**Production equivalent:** SSH to node → systemctl status kubelet
  → journalctl -u kubelet -n 50

## Scenario 4: Pending Pods — Resource Starvation
**Signal:** Pod stuck in Pending immediately on creation
**Root cause:** Resource requests exceed all node capacity
**Diagnostic commands:**
- kubectl describe pod → 0/3 nodes available: Insufficient cpu/memory
- kubectl describe nodes | grep -A8 "Allocated resources"
**Fix:** Reduce resource requests to realistic values
**Severity:** Medium — workload not running but no data loss
**Production equivalent:** Review resource quotas and node capacity planning

## Scenario 5: Service Selector Mismatch
**Signal:** Service endpoints show none — traffic not routing
**Root cause:** Service selector label does not match pod labels
**Diagnostic commands:**
- kubectl get endpoints → none
- kubectl describe service → shows wrong selector label
- kubectl get pods --show-labels → confirms actual pod labels
**Fix:** Patch service selector to match actual pod labels
**Severity:** Low-Medium — pods healthy, only traffic routing broken
**Production equivalent:** Always verify selectors after copy-paste deployments

## Evaluation Framework — AI Response Red Flags
1. Jumping to fix before diagnosing root cause
2. kubectl delete pod as first response to any failure
3. Assuming single root cause without elimination
4. Commands with wrong flags or resource names that would fail if run
5. No verification step after applying the fix

## Gold Standard Diagnosis Structure
1. Identify the exact symptom and pod/node status
2. List possible causes for that symptom
3. Run diagnostic commands to confirm which cause is active
4. Apply targeted fix based on confirmed cause only
5. Verify fix with a follow-up check command
6. Document what was found and what was changed
