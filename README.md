# SecReviewAgent AI

SecReviewAgent AI is an Infrastructure-as-Code security review agent for Terraform and Kubernetes.
It parses IaC, builds architecture context, and produces reviewer-friendly security findings.

It is also the flagship measurable workflow for
[Secure Context Cache](https://github.com/krishnamuppidi/secure-context-cache), an open-source
secure token-optimization framework. The integration pattern replaces oversized repository prompts
with a task-scoped capsule containing only the IAM, network, policy, ownership, environment, and
dependency facts approved for that review.

## Why Pair It with Secure Context Cache?

- Reduce repeated input tokens for Terraform and Kubernetes reviews.
- Preserve must-find security context and reject savings that weaken review quality.
- Keep unrelated topology and restricted context outside the model prompt.
- Compare changed-files-only, full-context, and governed-capsule review paths using provider usage,
  recall, precision, latency, cost, and reviewer acceptance.

**Product website:** https://krishnamuppidi.github.io/secreviewagent-ai/

**Foundational framework:** https://krishnamuppidi.github.io/secure-context-cache/

## Contents

- `src/secreviewagent/` - Core parsers, review agent, security knowledge, CLI, and webhook code.
- `src/lambda/` - AWS Lambda webhook handler with S3-backed repository memory.
- `infra/` - Terraform deployment template and example variable file.
- `examples/` - Small Terraform fixture for local review.
- `tests/` - Parser and behavior tests.
- `site/` - Product website, technical guides, machine-readable documentation, and analytics.
- `scripts/build_website.py` - Deterministic static-site generator.

Excluded from this clean code copy: generated artifacts, Terraform state, real tfvars,
caches, packaged zip files, and private deployment outputs.

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Run a local review:

```bash
secreview analyze examples/terraform --type terraform
```

Build and validate the website:

```bash
python scripts/build_website.py
pytest -q
```

## Disclaimer

The views and opinions expressed in this repository are solely those of the author and do not
represent or reflect the views, positions, policies, or opinions of the author's employer or any
affiliated organization. The content is provided for informational purposes only.
