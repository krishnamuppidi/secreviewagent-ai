# SecReviewAgent

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

SecReviewAgent is an open-source, context-aware security review system for Terraform and Kubernetes. It preserves repository architecture memory across pull requests and returns structured, reviewer-ready findings.

## Capabilities

- Terraform resource, reference, IAM policy, and security-group parsing.
- Kubernetes workload, RBAC, service-account, IRSA, ingress, and NetworkPolicy parsing.
- Pull-request diff analysis with architecture context.
- Structured findings with affected resources and actionable recommendations.
- AWS serverless webhook reference deployment.
- Human approval remains required.

## Research status

The SecReviewAgent paper was accepted and presented at ICUFN 2026. The website describes the design and public implementation without reproducing paper results as product claims.

## Token optimization

SecReviewAgent measures candidate context, selects approved security facts, reuses versioned architecture memory, uses provider prompt caching or optional compression where appropriate, and verifies that required findings and review quality are preserved.

## Guides

- [SecReviewAgent Use Cases for IaC and Cloud Security Review](https://krishnamuppidi.github.io/secreviewagent-ai/use-cases/index.md)
- [SecReviewAgent Examples: Terraform, IAM, Security Groups, and Kubernetes](https://krishnamuppidi.github.io/secreviewagent-ai/examples/index.md)
- [SecReviewAgent Documentation: Install, Run, Integrate, and Deploy](https://krishnamuppidi.github.io/secreviewagent-ai/docs/index.md)
- [Context-Aware Terraform Security Review with SecReviewAgent](https://krishnamuppidi.github.io/secreviewagent-ai/terraform-security-review/index.md)
- [Kubernetes Manifest Security Review with Architecture Context](https://krishnamuppidi.github.io/secreviewagent-ai/kubernetes-security-review/index.md)
- [AI-Assisted IAM Policy Analysis with Repository Context](https://krishnamuppidi.github.io/secreviewagent-ai/iam-policy-analysis/index.md)
- [What Is Context-Aware Infrastructure-as-Code Security Review?](https://krishnamuppidi.github.io/secreviewagent-ai/context-aware-iac-security/index.md)
- [Persistent Architecture Memory for DevSecOps and AI Code Review](https://krishnamuppidi.github.io/secreviewagent-ai/architecture-memory-devsecops/index.md)
- [AI Code Review Token Optimization for Terraform and Kubernetes](https://krishnamuppidi.github.io/secreviewagent-ai/ai-code-review-token-optimization/index.md)
- [AI Code Review vs Static Analysis for Infrastructure-as-Code](https://krishnamuppidi.github.io/secreviewagent-ai/ai-code-review-vs-static-analysis/index.md)
- [Checkov vs SecReviewAgent: Rules and Context for IaC Security](https://krishnamuppidi.github.io/secreviewagent-ai/checkov-vs-secreviewagent/index.md)
- [tfsec vs SecReviewAgent for Terraform Security Review](https://krishnamuppidi.github.io/secreviewagent-ai/tfsec-vs-secreviewagent/index.md)
- [Secure AI Code Review: Least-Privilege Context for IaC](https://krishnamuppidi.github.io/secreviewagent-ai/secure-ai-code-review/index.md)
- [Infrastructure-as-Code Security Review Checklist](https://krishnamuppidi.github.io/secreviewagent-ai/iac-security-review-checklist/index.md)
- [SecReviewAgent Research, Evaluation Method, and Claim Boundaries](https://krishnamuppidi.github.io/secreviewagent-ai/research/index.md)
- [About SecReviewAgent and Naga Krishna Reddy Muppidi](https://krishnamuppidi.github.io/secreviewagent-ai/about/index.md)
