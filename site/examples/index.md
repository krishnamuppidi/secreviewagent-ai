# SecReviewAgent Examples: Terraform, IAM, Security Groups, and Kubernetes

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/examples/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

Each example traces the changed configuration, the additional context, the resulting risk statement, and a reviewer-ready remediation.

## Example 1: read-only IAM permission with a risky trust path

        Changed line"s3:GetObject"
+Stored contextcross-account trust → prod-risk-data/*
=Findingexternal read path to sensitive data

        A diff-only review may treat read access as low risk. SecReviewAgent can combine the action, target resource, trust policy, and repository data-path description. The finding should state exactly which role can be assumed, which prefix is reachable, and why that prefix matters. A useful recommendation may narrow the principal, require an external ID, constrain the prefix, and add an explicit deny for unapproved environments.

## Example 2: public SSH rule

```
ingress {
  protocol    = "tcp"
  from_port   = 22
  to_port     = 22
  cidr_blocks = ["0.0.0.0/0"]
}
```

        The Terraform parser marks this rule public and preserves the actual ports and CIDR. The review output can name the affected security group and recommend a private access path, a managed session service, or a constrained administrative CIDR. This is a deterministic issue, so a static scanner should remain the primary control; SecReviewAgent adds an explanation tied to the surrounding workload.

## Example 3: Kubernetes cluster-wide privilege

```
kind: ClusterRoleBinding
subjects:
  - kind: ServiceAccount
    name: deployer
roleRef:
  kind: ClusterRole
  name: cluster-admin
```

        The Kubernetes parser connects the service account to the binding. If IRSA annotations and workload references are also present, the reviewer can evaluate both Kubernetes and cloud privilege. The remediation may replace the cluster-wide role with a namespace-scoped Role, restrict verbs and resources, and separate deployment automation from runtime identity.

## What a good output contains

        SecReviewAgent returns an architecture summary, service interactions, resource-specific explanations, severity-ranked findings, affected resource addresses, concept references, and actionable recommendations. The output remains evidence for a human decision—not an autonomous approval or deployment command.

        [Run the included Terraform fixture and inspect the JSON contract →](../docs/)
