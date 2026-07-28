# SecReviewAgent Use Cases for IaC and Cloud Security Review

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/use-cases/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

SecReviewAgent complements deterministic scanners by explaining how a change interacts with repository architecture, identity, networking, and data paths.

## Supported in the public implementation

          Terraform
### Cross-resource Terraform review
Parse resources, references, IAM statements, security groups, and public network rules. The review output names affected resource addresses and the configuration values behind each concern.
[See the Terraform workflow →](../terraform-security-review/)

          Kubernetes
### Workload, RBAC, and network review
Parse workloads, service accounts, IRSA annotations, role bindings, ingress and egress policy, then explain how those pieces combine.
[See the Kubernetes workflow →](../kubernetes-security-review/)

          Pull requests
### Context-aware PR review
Accept a Git diff, isolate added, removed, and modified infrastructure, and return structured findings suitable for a human reviewer.
[Understand context-aware review →](../context-aware-iac-security/)

          AWS
### Serverless webhook deployment
Deploy an API Gateway and Lambda review path with repository memory stored in S3. Secrets remain in managed configuration rather than source.
[Open deployment documentation →](../docs/)

## High-value review scenarios

        A narrow permission can become dangerous through an existing trust relationship. A Kubernetes workload can bypass an expected boundary through hostNetwork, a privileged security context, or a service account with broader cloud access. A security group change can expose a data path that is not visible in the changed file. These are the scenarios where architecture memory adds the most value.

        - IAM permissions combined with role trust and downstream data stores.
- Public ingress combined with sensitive workloads or administrative ports.
- Kubernetes RBAC combined with workload identity and cluster-wide bindings.
- Pull-request changes that alter an existing cross-resource privilege path.
- Repeated reviews where repository context can be loaded instead of rebuilt.

## Token-optimized review

        Repeated IaC review should not resend an entire repository on every pull request. SecReviewAgent can measure the candidate prompt, select the security-relevant resource and architecture facts, reuse versioned repository memory, use provider prompt caching where available, and verify that a smaller context still preserves required findings. Token reduction counts only when review quality passes the defined gate.

        [See the token-optimization workflow →](../ai-code-review-token-optimization/)

## Roadmap integrations, clearly labeled

        CloudFormation, Pulumi, Helm, Kustomize, GitHub Actions, GitLab CI, Jenkins, OPA/Rego, Dockerfiles, and SBOM-aware supply-chain review are useful expansion targets. They are not presented as current parser support. The architecture can accommodate them through additional parsers and evidence adapters, but each integration needs tests, fixtures, and an evaluation before it becomes a supported claim.
