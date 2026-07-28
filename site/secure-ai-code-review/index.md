# Secure AI Code Review: Least-Privilege Context for IaC

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/secure-ai-code-review/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

Security review can create a new data-exposure path if repository context, secrets, and architecture memory are not governed before model invocation.

## Bound the context before inference

        Changed files alone may be insufficient, but whole-repository prompts are not the only alternative. Select the IAM, network, data, ownership, and dependency facts required for the review. Deny unrelated repositories, secret-adjacent content, and broad topology. Record why each slice was released.

## Minimum controls

        - Workload authentication and repository-scoped authorization.
- Secret, credential, token, and sensitive-literal redaction.
- Encrypted context storage with schema and freshness metadata.
- Source hashes, selected facts, denied facts, and model version in the audit record.
- Human approval for merge, policy exceptions, and production actions.
- Retention and deletion controls for repository memory and prompts.

## Fail closed on missing authorization

        If the reviewer cannot obtain an approved context set, it should stop or fall back to an explicitly limited diff-only review. It should not silently query broad stores or reuse context from another repository, tenant, or environment.

## Measure security and quality together

        Track prohibited-context release, required-fact coverage, finding precision and recall, reviewer acceptance, latency, and token usage. A cheaper prompt is not an improvement if it misses a required security fact. A higher recall is not acceptable if it exposes unauthorized repository content.

        SecReviewAgent can use [Secure Context Cache](https://krishnamuppidi.github.io/secure-context-cache/) as the context-release layer for this design.
