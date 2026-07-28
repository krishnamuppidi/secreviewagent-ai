# AI-Assisted IAM Policy Analysis with Repository Context

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/iam-policy-analysis/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

SecReviewAgent preserves IAM actions and resources, then places them beside trust relationships, workloads, and data paths.

## Why local IAM checks are not enough

        Wildcards, administrative actions, and public principals are important deterministic signals. But a policy can be risky without using *. The security meaning of s3:GetObject, kms:Decrypt, iam:PassRole, or sts:AssumeRole depends on the target resource, trusted principal, condition keys, and the identities that can reach the role.

## A practical review sequence

        - Normalize allowed and denied actions, resources, principals, and conditions.
- Resolve Terraform references and role attachments.
- Trace assume-role, pass-role, workload-identity, and data-access paths.
- Classify the affected environment and data sensitivity.
- Recommend a narrower principal, action, resource, condition, or session boundary.

## Example reviewer language

        Context-dependent high severityThe new deployment role can pass prod-reporting-role to Lambda. That target role already grants decryption and read access to the production reporting bucket. Restrict iam:PassRole to the intended runtime role and enforce the expected service through iam:PassedToService.

        The important detail is the complete privilege path. A reviewer can confirm or reject the path because the finding names the roles, downstream permission, and proposed condition.

## Human and policy gates remain mandatory

        Use IAM Access Analyzer, organization policies, policy-as-code, and cloud audit data as authoritative inputs. Treat model reasoning as an explainable review layer. Never let the model directly attach policies or approve privileged infrastructure.
