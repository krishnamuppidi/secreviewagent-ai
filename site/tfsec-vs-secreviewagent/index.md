# tfsec vs SecReviewAgent for Terraform Security Review

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/tfsec-vs-secreviewagent/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

tfsec and related Trivy configuration checks detect known Terraform risks; SecReviewAgent is designed for relationships that require stored architecture context.

## Deterministic Terraform scanning

        tfsec became a familiar choice because it maps Terraform configuration to concrete security checks with fast local and CI execution. Today many teams consume that capability through Trivy configuration scanning. This remains a strong control for known insecure values and resource patterns.

## Context-aware review

        SecReviewAgent parses Terraform resources and references, builds an architecture view, and asks how the pull request changes existing trust, network, or data paths. A new route, role, or attachment can be risky because of resources that were not edited. This is the gap persistent memory is intended to address.

## Use both without creating noise

        Start with deterministic results. Mark them as scanner evidence. Run contextual reasoning only on security-relevant deltas and the minimum approved architecture facts. Merge exact duplicates, but do not let a model suppress a scanner failure silently. Route uncertain relationship findings to a human with the relevant resource graph.

## Selection guide

        - Need fast known checks in every commit? Use deterministic scanning.
- Need custom organization policy? Add policy-as-code.
- Need a cross-file trust or data-path explanation? Add context-aware review.
- Need merge enforcement? Base it on validated rules and explicit human decisions.
- Need evidence of improvement? Evaluate all paths on the same labeled PR set.
