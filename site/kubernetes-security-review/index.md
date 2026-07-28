# Kubernetes Manifest Security Review with Architecture Context

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/kubernetes-security-review/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

A Kubernetes finding becomes more useful when the reviewer can see the workload, service account, role binding, policy, and external data path together.

## Supported Kubernetes evidence

        SecReviewAgent parses multi-document YAML and models Deployments, StatefulSets, DaemonSets, Jobs, CronJobs, Pods, Services, Ingress objects, NetworkPolicies, ServiceAccounts, Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings. It records namespace, labels, annotations, specifications, IRSA role ARNs, and binding relationships.

## Context-dependent risks

        A privileged container is often detectable from one manifest. The architectural question is what that container can reach. A service account bound to cluster-admin may also assume an AWS role. A public ingress may lead to a workload that can query an internal data service. A missing egress policy matters differently for an isolated batch job and an internet-facing identity service.

        - Connect workload service accounts to namespaced and cluster-wide RBAC.
- Connect IRSA annotations to cloud permissions and target resources.
- Evaluate ingress and egress together with workload sensitivity.
- Flag privilege, host access, and policy bypass with the relevant namespace.
- Distinguish absent policy from explicitly broad policy.

## Review output for humans

        A useful Kubernetes review names the manifest and resource, quotes the risky value, describes the path it creates, and proposes the smallest safe change. It does not merely say “RBAC is too broad.” It should state which service account receives which role and whether the scope can be reduced.

## What is next

        Helm and Kustomize are roadmap integrations. Until rendered-manifest and overlay tests are added, teams can render those configurations in CI and pass the resulting YAML to the existing Kubernetes parser. That workflow should be documented as an integration pattern, not native parser support.
