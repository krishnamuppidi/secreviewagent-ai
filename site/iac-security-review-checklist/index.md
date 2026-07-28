# Infrastructure-as-Code Security Review Checklist

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/iac-security-review-checklist/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

Use deterministic controls first, then evaluate architecture relationships, deployment impact, and the evidence behind any AI-generated finding.

## Identity and access
- Are actions, resources, principals, and trust conditions narrowly scoped?
- Can any identity pass or assume a more privileged role?
- Do workload identities match the intended namespace, service, account, and environment?
- Are policy exceptions explicit, time-bounded, and owned?

## Network and data paths
- Does ingress expose public or administrative ports?
- Is egress constrained for sensitive workloads?
- Do routes, endpoints, load balancers, and security groups preserve segmentation?
- Are storage, database, and key-management resources encrypted and access-scoped?

## Kubernetes and containers
- Are privileged mode, host namespaces, host paths, and unsafe capabilities disabled?
- Are RBAC bindings namespaced and verb/resource scopes minimal?
- Do NetworkPolicies cover both ingress and egress where required?
- Are images pinned, scanned, and promoted with verifiable provenance?

## AI-assisted review controls
- Was the context authorized for this repository and task?
- Were secrets and sensitive literals removed before inference?
- Does every finding cite a resource and configuration value?
- Are deterministic scanner results distinguishable from model reasoning?
- Is a human responsible for the final merge or exception decision?

## Evidence to retain
Preserve the pull-request commit, scanner versions, policy bundle, selected context version, model and prompt version, structured findings, reviewer disposition, remediation commit, and final approval. This turns review from a comment stream into auditable engineering evidence.
