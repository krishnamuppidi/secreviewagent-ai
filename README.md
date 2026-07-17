# SecReviewAgent AI

SecReviewAgent AI is an Infrastructure-as-Code security review agent for Terraform and Kubernetes.
It parses IaC, builds architecture context, and produces reviewer-friendly security findings.

## Contents

- `src/secreviewagent/` - Core parsers, review agent, security knowledge, CLI, and webhook code.
- `src/lambda/` - AWS Lambda webhook handler with S3-backed repository memory.
- `infra/` - Terraform deployment template and example variable file.
- `examples/` - Small Terraform fixture for local review.
- `tests/` - Parser and behavior tests.

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

## Disclaimer

The views and opinions expressed in this repository are solely those of the author and do not
represent or reflect the views, positions, policies, or opinions of the author's employer or any
affiliated organization. The content is provided for informational purposes only.
