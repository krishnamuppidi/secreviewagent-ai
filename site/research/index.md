# SecReviewAgent Research, Evaluation Method, and Claim Boundaries

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/research/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

The SecReviewAgent paper was accepted and presented at ICUFN 2026. This page separates paper-reported results from guarantees about the public prototype.

## Research contribution

        The paper, SecReviewAgent: Context-Aware Security Review of Infrastructure-as-Code Using Persistent Architecture Memory, presents a repository memory design, cold and warm review algorithms, Terraform and Kubernetes parsing, structured findings, and an empirical comparison focused on context-dependent security issues.

        The work was accepted and presented at the 2026 International Conference on Ubiquitous and Future Networks (ICUFN). The conference manuscript names Naga Krishna Reddy Muppidi, Veera Ravindra Divi, Sneha Gullapalli, and Rambabu Pasumarthy as authors.

## Results reported in the paper

        847IaC pull requests
23repositories
0.89precision
0.83F1
2.4×context-dependent recall vs no-context baseline
73%warm-review latency reduction

        These are manuscript-reported research results under the paper’s dataset, labeling process, baselines, and implementation. They are not universal production guarantees.

## Evaluation design

        The manuscript describes comparisons with deterministic scanners and a no-context model, dual security labeling with adjudication, separate context-dependent recall analysis, cold and warm latency measurement, and a controlled practitioner study. The design is intended to test the specific mechanism: whether persistent repository context improves review of relational infrastructure risks.

## Limitations and reproducibility

        Private repositories cannot be redistributed. Aggregate statistics and methodology do not substitute for a public benchmark corpus. Model behavior, prompt design, parser quality, and baseline configuration can affect results. Architecture memory can become stale. Cross-repository systems are only partially modeled. Human review remains necessary.

        [Read the conference manuscript](../assets/secreviewagent-icufn-2026-paper.pdf)
