# Context-Aware Terraform Security Review with SecReviewAgent

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/terraform-security-review/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

SecReviewAgent parses actual HCL values and resource references so findings can explain IAM, networking, data, and compute relationships.

## What the Terraform parser extracts

        The public implementation reads .tf and .tf.json, captures resource type, name, address, attributes, and references, and classifies common AWS compute, storage, identity, and network resources. IAM policy statements are normalized into allowed actions and resources. Security-group rules preserve direction, protocol, port range, CIDRs, source groups, and public-access state.

        This structured context lets the model cite an actual resource address and configuration value. It also makes review output easier to test than a generic prompt that receives a folder of text.

## Questions a context-aware Terraform review should answer

        - Does a new principal inherit access through an existing assume-role chain?
- Does a narrow action reach a sensitive bucket, table, secret, or encryption key?
- Does a new network rule expose a workload with privileged downstream access?
- Does a module reference change a production data path outside the edited file?
- Is the finding deterministic, contextual, or uncertain—and is that distinction visible?

## Use alongside Checkov, tfsec, and policy-as-code

        SecReviewAgent is not positioned as a replacement for deterministic scanning. Checkov, tfsec, Terrascan, KICS, Sentinel, and OPA remain valuable for known controls. The context-aware layer should consume their evidence, reason about cross-resource implications, and produce an explanation a reviewer can challenge.

        [Compare deterministic and contextual review →](../checkov-vs-secreviewagent/)

## Safe operating model

        Limit repository scope, redact sensitive literals, store architecture memory in encrypted storage, version its schema, expire stale facts, and keep merge authority outside the model. Measure precision, recall, latency, and reviewer acceptance on your own labeled pull requests before changing enforcement.
