# AI Code Review Token Optimization for Terraform and Kubernetes

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/ai-code-review-token-optimization/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

SecReviewAgent makes token optimization measurable: count the full candidate context, assemble the minimum approved review capsule, reuse stable architecture facts, and accept savings only when finding quality holds.

## Why IaC reviews repeat expensive context

        A pull request may change only a few Terraform resources or Kubernetes manifests, while the security decision still depends on IAM relationships, network boundaries, ownership, environment, data classification, and existing dependencies. Sending the whole repository provides breadth but repeats many unchanged tokens. Sending only the diff is cheaper but can omit the facts that make a risk visible.

        The useful middle path is a task-scoped context capsule: the changed resources plus only the approved architecture facts required to review them.

## Measure → Select → Reuse → Cache → Verify

        1. MeasureCount the full candidate prompt with a model-aware tokenizer.
2. SelectChoose relevant IAM, network, policy, ownership, environment, and dependency facts.
3. ReuseLoad versioned architecture memory instead of rebuilding repository understanding.
4. Cache or compressUse provider prompt caching and optional compression only where they preserve meaning.
5. VerifyCompare required-fact coverage, findings, false positives, reviewer acceptance, latency, and provider usage.

## Stable context and changing context

        Separate repository knowledge into stable and dynamic layers. Resource relationships, ownership, architecture summaries, and approved policy explanations may remain stable across many reviews. The pull-request diff, current scanner findings, environment changes, and expiring exceptions are dynamic. Keeping the stable prefix consistent can improve provider cacheability while the dynamic suffix stays specific to the task.

## Security controls are part of optimization

        Fewer tokens do not automatically mean safer prompts. Selection must occur after workload authentication and policy evaluation. The capsule should carry provenance, source hashes, freshness, policy version, and an audit identifier. Unrelated topology and secret-adjacent material should remain outside the model boundary.

        SecReviewAgent uses [Secure Context Cache](https://krishnamuppidi.github.io/secure-context-cache/) as the foundational framework for measurement, selection, reusable context, provider caching, optional compression, routing, and quality verification.

## How to prove savings responsibly

        Replay the same labeled pull requests through changed-files-only, full approved context, and optimized capsule paths. Use provider-reported input usage where possible. Record finding precision and recall, required-fact coverage, prohibited-context release, reviewer acceptance, latency, and cost. Report a reduction only for reviews that meet the agreed quality and security thresholds.

        No universal percentageToken savings depend on repository size, change shape, model tokenizer, provider caching, policy scope, and the quality gate. This site does not present one fixed savings percentage.
