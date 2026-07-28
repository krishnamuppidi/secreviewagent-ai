# SecReviewAgent Documentation: Install, Run, Integrate, and Deploy

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/docs/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

Use the public Python package, CLI, webhook service, and Terraform deployment template as an inspectable reference implementation.

## Local installation

```
git clone https://github.com/krishnamuppidi/secreviewagent-ai.git
cd secreviewagent-ai
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

        The package requires Python 3.10 or newer. Configure ANTHROPIC_API_KEY outside source control before invoking model-backed analysis.

## Run a Terraform review

```
secreview analyze examples/terraform --type terraform
```

        The parser walks .tf and .tf.json files, extracts resources and references, expands IAM policy statements, identifies public security-group rules, and sends structured configuration—not an opaque repository dump—to the reviewer model.

## Run a Kubernetes review

```
secreview analyze path/to/manifests --type kubernetes
```

        Kubernetes analysis accepts YAML manifests and models workloads, services, ingress, service accounts, IRSA role annotations, RBAC bindings, and NetworkPolicy relationships.

## Output contract

        The stable review shape contains architecture_summary, service_explanations, service_interactions, and security_findings. Each finding includes severity, title, description, affected resources, a recommendation, and related security concepts. Consumers should validate the JSON, preserve source references, and keep a human approval step.

## AWS webhook deployment

        The infrastructure template deploys the review handler behind API Gateway and Lambda, with S3-backed repository memory. Review infra/terraform.tfvars.example, keep real values and state out of version control, build the Lambda layer, run terraform plan, and require an operator to approve the production apply.

        Security boundaryNever place cloud credentials, repository tokens, model keys, or raw secrets in prompts. Redact sensitive literals, scope repository access, encrypt stored context, and retain auditable review records.
