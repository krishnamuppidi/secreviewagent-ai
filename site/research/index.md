# SecReviewAgent Research, Evaluation Method, and Claim Boundaries

Canonical URL: https://krishnamuppidi.github.io/secreviewagent-ai/research/
Source code: https://github.com/krishnamuppidi/secreviewagent-ai

The SecReviewAgent paper was accepted and presented at ICUFN 2026. The public site focuses on the design, implementation, and responsible-use boundaries rather than reproducing paper results.

## Research contribution

        The paper, SecReviewAgent: Context-Aware Security Review of Infrastructure-as-Code Using Persistent Architecture Memory, presents a repository memory design, cold and warm review algorithms, Terraform and Kubernetes parsing, structured findings, and an empirical comparison focused on context-dependent security issues.

        The work was accepted and presented at the 2026 International Conference on Ubiquitous and Future Networks (ICUFN). The conference manuscript names Naga Krishna Reddy Muppidi, Veera Ravindra Divi, Sneha Gullapalli, and Rambabu Pasumarthy as authors.

## From research design to public implementation

        The public repository implements the core review path: Terraform and Kubernetes parsing, structured infrastructure context, pull-request diff review, reviewer-friendly findings, a webhook service, and an AWS deployment template. It also connects the application to Secure Context Cache so repeated reviews can use measured, task-scoped context instead of repeatedly sending broad repository prompts.

## Responsible-use boundaries

        The conference manuscript documents the research method and results; this website does not reproduce those results as product claims. Model behavior, prompt design, parser quality, repository shape, and policy configuration affect every deployment. Architecture memory can become stale, cross-repository systems are only partially modeled, and token savings vary by workload. Human review remains necessary.

        [Read the conference manuscript](../assets/secreviewagent-icufn-2026-paper.pdf)
