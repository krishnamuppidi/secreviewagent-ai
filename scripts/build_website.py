#!/usr/bin/env python3
"""Build the static SecReviewAgent product and research website."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://krishnamuppidi.github.io/secreviewagent-ai/"
REPOSITORY = "https://github.com/krishnamuppidi/secreviewagent-ai"
AUTHOR = "Naga Krishna Reddy Muppidi"
TODAY = "2026-07-28"


@dataclass(frozen=True)
class Page:
    route: str
    title: str
    description: str
    eyebrow: str
    heading: str
    lead: str
    body: str
    keywords: tuple[str, ...]


PAGES = (
    Page(
        "use-cases/",
        "SecReviewAgent Use Cases for IaC and Cloud Security Review",
        "Explore supported and roadmap use cases for context-aware Terraform, Kubernetes, IAM, network, and pull-request security review.",
        "Use-case map",
        "Review infrastructure changes with the context each decision requires.",
        "SecReviewAgent complements deterministic scanners by explaining how a change interacts with repository architecture, identity, networking, and data paths.",
        """
        <section class="content-section"><h2>Supported in the public implementation</h2>
        <div class="card-grid">
          <article class="info-card"><span>Terraform</span><h3>Cross-resource Terraform review</h3><p>Parse resources, references, IAM statements, security groups, and public network rules. The review output names affected resource addresses and the configuration values behind each concern.</p><a href="../terraform-security-review/">See the Terraform workflow →</a></article>
          <article class="info-card"><span>Kubernetes</span><h3>Workload, RBAC, and network review</h3><p>Parse workloads, service accounts, IRSA annotations, role bindings, ingress and egress policy, then explain how those pieces combine.</p><a href="../kubernetes-security-review/">See the Kubernetes workflow →</a></article>
          <article class="info-card"><span>Pull requests</span><h3>Context-aware PR review</h3><p>Accept a Git diff, isolate added, removed, and modified infrastructure, and return structured findings suitable for a human reviewer.</p><a href="../context-aware-iac-security/">Understand context-aware review →</a></article>
          <article class="info-card"><span>AWS</span><h3>Serverless webhook deployment</h3><p>Deploy an API Gateway and Lambda review path with repository memory stored in S3. Secrets remain in managed configuration rather than source.</p><a href="../docs/">Open deployment documentation →</a></article>
        </div></section>
        <section class="content-section"><h2>High-value review scenarios</h2>
        <p>A narrow permission can become dangerous through an existing trust relationship. A Kubernetes workload can bypass an expected boundary through <code>hostNetwork</code>, a privileged security context, or a service account with broader cloud access. A security group change can expose a data path that is not visible in the changed file. These are the scenarios where architecture memory adds the most value.</p>
        <ul class="check-list"><li>IAM permissions combined with role trust and downstream data stores.</li><li>Public ingress combined with sensitive workloads or administrative ports.</li><li>Kubernetes RBAC combined with workload identity and cluster-wide bindings.</li><li>Pull-request changes that alter an existing cross-resource privilege path.</li><li>Repeated reviews where repository context can be loaded instead of rebuilt.</li></ul></section>
        <section class="content-section"><h2>Roadmap integrations, clearly labeled</h2>
        <p>CloudFormation, Pulumi, Helm, Kustomize, GitHub Actions, GitLab CI, Jenkins, OPA/Rego, Dockerfiles, and SBOM-aware supply-chain review are useful expansion targets. They are not presented as current parser support. The architecture can accommodate them through additional parsers and evidence adapters, but each integration needs tests, fixtures, and an evaluation before it becomes a supported claim.</p></section>
        """,
        ("IaC security review use cases", "Terraform security review", "Kubernetes security review", "AI DevSecOps"),
    ),
    Page(
        "examples/",
        "SecReviewAgent Examples: Terraform, IAM, Security Groups, and Kubernetes",
        "Walk through practical SecReviewAgent examples for Terraform IAM permissions, public security groups, Kubernetes RBAC, and network policies.",
        "Worked examples",
        "See the difference between a local rule and an architectural finding.",
        "Each example traces the changed configuration, the additional context, the resulting risk statement, and a reviewer-ready remediation.",
        """
        <section class="content-section"><h2>Example 1: read-only IAM permission with a risky trust path</h2>
        <div class="example-flow"><div><b>Changed line</b><code>"s3:GetObject"</code></div><i>+</i><div><b>Stored context</b><code>cross-account trust → prod-risk-data/*</code></div><i>=</i><div class="danger"><b>Finding</b><code>external read path to sensitive data</code></div></div>
        <p>A diff-only review may treat read access as low risk. SecReviewAgent can combine the action, target resource, trust policy, and repository data-path description. The finding should state exactly which role can be assumed, which prefix is reachable, and why that prefix matters. A useful recommendation may narrow the principal, require an external ID, constrain the prefix, and add an explicit deny for unapproved environments.</p></section>
        <section class="content-section"><h2>Example 2: public SSH rule</h2>
        <pre><code>ingress {
  protocol    = "tcp"
  from_port   = 22
  to_port     = 22
  cidr_blocks = ["0.0.0.0/0"]
}</code></pre>
        <p>The Terraform parser marks this rule public and preserves the actual ports and CIDR. The review output can name the affected security group and recommend a private access path, a managed session service, or a constrained administrative CIDR. This is a deterministic issue, so a static scanner should remain the primary control; SecReviewAgent adds an explanation tied to the surrounding workload.</p></section>
        <section class="content-section"><h2>Example 3: Kubernetes cluster-wide privilege</h2>
        <pre><code>kind: ClusterRoleBinding
subjects:
  - kind: ServiceAccount
    name: deployer
roleRef:
  kind: ClusterRole
  name: cluster-admin</code></pre>
        <p>The Kubernetes parser connects the service account to the binding. If IRSA annotations and workload references are also present, the reviewer can evaluate both Kubernetes and cloud privilege. The remediation may replace the cluster-wide role with a namespace-scoped Role, restrict verbs and resources, and separate deployment automation from runtime identity.</p></section>
        <section class="content-section"><h2>What a good output contains</h2>
        <p>SecReviewAgent returns an architecture summary, service interactions, resource-specific explanations, severity-ranked findings, affected resource addresses, concept references, and actionable recommendations. The output remains evidence for a human decision—not an autonomous approval or deployment command.</p>
        <p><a class="text-link" href="../docs/">Run the included Terraform fixture and inspect the JSON contract →</a></p></section>
        """,
        ("Terraform security example", "IAM policy analysis example", "Kubernetes RBAC review", "security group review"),
    ),
    Page(
        "docs/",
        "SecReviewAgent Documentation: Install, Run, Integrate, and Deploy",
        "Install SecReviewAgent, run Terraform and Kubernetes reviews, understand structured findings, and deploy the AWS webhook architecture.",
        "Documentation",
        "From local IaC analysis to a review webhook.",
        "Use the public Python package, CLI, webhook service, and Terraform deployment template as an inspectable reference implementation.",
        """
        <section class="content-section"><h2>Local installation</h2>
        <pre><code>git clone https://github.com/krishnamuppidi/secreviewagent-ai.git
cd secreviewagent-ai
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q</code></pre>
        <p>The package requires Python 3.10 or newer. Configure <code>ANTHROPIC_API_KEY</code> outside source control before invoking model-backed analysis.</p></section>
        <section class="content-section"><h2>Run a Terraform review</h2>
        <pre><code>secreview analyze examples/terraform --type terraform</code></pre>
        <p>The parser walks <code>.tf</code> and <code>.tf.json</code> files, extracts resources and references, expands IAM policy statements, identifies public security-group rules, and sends structured configuration—not an opaque repository dump—to the reviewer model.</p></section>
        <section class="content-section"><h2>Run a Kubernetes review</h2>
        <pre><code>secreview analyze path/to/manifests --type kubernetes</code></pre>
        <p>Kubernetes analysis accepts YAML manifests and models workloads, services, ingress, service accounts, IRSA role annotations, RBAC bindings, and NetworkPolicy relationships.</p></section>
        <section class="content-section"><h2>Output contract</h2>
        <p>The stable review shape contains <code>architecture_summary</code>, <code>service_explanations</code>, <code>service_interactions</code>, and <code>security_findings</code>. Each finding includes severity, title, description, affected resources, a recommendation, and related security concepts. Consumers should validate the JSON, preserve source references, and keep a human approval step.</p></section>
        <section class="content-section"><h2>AWS webhook deployment</h2>
        <p>The infrastructure template deploys the review handler behind API Gateway and Lambda, with S3-backed repository memory. Review <code>infra/terraform.tfvars.example</code>, keep real values and state out of version control, build the Lambda layer, run <code>terraform plan</code>, and require an operator to approve the production apply.</p>
        <div class="notice"><b>Security boundary</b><p>Never place cloud credentials, repository tokens, model keys, or raw secrets in prompts. Redact sensitive literals, scope repository access, encrypt stored context, and retain auditable review records.</p></div></section>
        """,
        ("SecReviewAgent documentation", "IaC security CLI", "Terraform AI review setup", "Kubernetes security review tool"),
    ),
    Page(
        "terraform-security-review/",
        "Context-Aware Terraform Security Review with SecReviewAgent",
        "Review Terraform resources, IAM policies, security groups, references, and pull-request changes with repository-aware AI explanations.",
        "Terraform security review",
        "Review what a Terraform change means—not only what its line contains.",
        "SecReviewAgent parses actual HCL values and resource references so findings can explain IAM, networking, data, and compute relationships.",
        """
        <section class="content-section"><h2>What the Terraform parser extracts</h2>
        <p>The public implementation reads <code>.tf</code> and <code>.tf.json</code>, captures resource type, name, address, attributes, and references, and classifies common AWS compute, storage, identity, and network resources. IAM policy statements are normalized into allowed actions and resources. Security-group rules preserve direction, protocol, port range, CIDRs, source groups, and public-access state.</p>
        <p>This structured context lets the model cite an actual resource address and configuration value. It also makes review output easier to test than a generic prompt that receives a folder of text.</p></section>
        <section class="content-section"><h2>Questions a context-aware Terraform review should answer</h2>
        <ul class="check-list"><li>Does a new principal inherit access through an existing assume-role chain?</li><li>Does a narrow action reach a sensitive bucket, table, secret, or encryption key?</li><li>Does a new network rule expose a workload with privileged downstream access?</li><li>Does a module reference change a production data path outside the edited file?</li><li>Is the finding deterministic, contextual, or uncertain—and is that distinction visible?</li></ul></section>
        <section class="content-section"><h2>Use alongside Checkov, tfsec, and policy-as-code</h2>
        <p>SecReviewAgent is not positioned as a replacement for deterministic scanning. Checkov, tfsec, Terrascan, KICS, Sentinel, and OPA remain valuable for known controls. The context-aware layer should consume their evidence, reason about cross-resource implications, and produce an explanation a reviewer can challenge.</p>
        <p><a class="text-link" href="../checkov-vs-secreviewagent/">Compare deterministic and contextual review →</a></p></section>
        <section class="content-section"><h2>Safe operating model</h2>
        <p>Limit repository scope, redact sensitive literals, store architecture memory in encrypted storage, version its schema, expire stale facts, and keep merge authority outside the model. Measure precision, recall, latency, and reviewer acceptance on your own labeled pull requests before changing enforcement.</p></section>
        """,
        ("Terraform security review", "AI Terraform code review", "Terraform IAM analysis", "Terraform PR security"),
    ),
    Page(
        "kubernetes-security-review/",
        "Kubernetes Manifest Security Review with Architecture Context",
        "Analyze Kubernetes workloads, RBAC, service accounts, IRSA, ingress, and network policies with contextual security explanations.",
        "Kubernetes security review",
        "Connect workload configuration, cluster privilege, network reachability, and cloud identity.",
        "A Kubernetes finding becomes more useful when the reviewer can see the workload, service account, role binding, policy, and external data path together.",
        """
        <section class="content-section"><h2>Supported Kubernetes evidence</h2>
        <p>SecReviewAgent parses multi-document YAML and models Deployments, StatefulSets, DaemonSets, Jobs, CronJobs, Pods, Services, Ingress objects, NetworkPolicies, ServiceAccounts, Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings. It records namespace, labels, annotations, specifications, IRSA role ARNs, and binding relationships.</p></section>
        <section class="content-section"><h2>Context-dependent risks</h2>
        <p>A privileged container is often detectable from one manifest. The architectural question is what that container can reach. A service account bound to <code>cluster-admin</code> may also assume an AWS role. A public ingress may lead to a workload that can query an internal data service. A missing egress policy matters differently for an isolated batch job and an internet-facing identity service.</p>
        <ul class="check-list"><li>Connect workload service accounts to namespaced and cluster-wide RBAC.</li><li>Connect IRSA annotations to cloud permissions and target resources.</li><li>Evaluate ingress and egress together with workload sensitivity.</li><li>Flag privilege, host access, and policy bypass with the relevant namespace.</li><li>Distinguish absent policy from explicitly broad policy.</li></ul></section>
        <section class="content-section"><h2>Review output for humans</h2>
        <p>A useful Kubernetes review names the manifest and resource, quotes the risky value, describes the path it creates, and proposes the smallest safe change. It does not merely say “RBAC is too broad.” It should state which service account receives which role and whether the scope can be reduced.</p></section>
        <section class="content-section"><h2>What is next</h2>
        <p>Helm and Kustomize are roadmap integrations. Until rendered-manifest and overlay tests are added, teams can render those configurations in CI and pass the resulting YAML to the existing Kubernetes parser. That workflow should be documented as an integration pattern, not native parser support.</p></section>
        """,
        ("Kubernetes security review", "Kubernetes manifest scanner AI", "RBAC security analysis", "IRSA security review"),
    ),
    Page(
        "iam-policy-analysis/",
        "AI-Assisted IAM Policy Analysis with Repository Context",
        "Analyze IAM actions, resources, trust paths, cross-account access, and infrastructure dependencies with SecReviewAgent context.",
        "IAM analysis",
        "Least privilege depends on both the statement and the architecture around it.",
        "SecReviewAgent preserves IAM actions and resources, then places them beside trust relationships, workloads, and data paths.",
        """
        <section class="content-section"><h2>Why local IAM checks are not enough</h2>
        <p>Wildcards, administrative actions, and public principals are important deterministic signals. But a policy can be risky without using <code>*</code>. The security meaning of <code>s3:GetObject</code>, <code>kms:Decrypt</code>, <code>iam:PassRole</code>, or <code>sts:AssumeRole</code> depends on the target resource, trusted principal, condition keys, and the identities that can reach the role.</p></section>
        <section class="content-section"><h2>A practical review sequence</h2>
        <ol class="number-list"><li><b>Normalize</b> allowed and denied actions, resources, principals, and conditions.</li><li><b>Resolve</b> Terraform references and role attachments.</li><li><b>Trace</b> assume-role, pass-role, workload-identity, and data-access paths.</li><li><b>Classify</b> the affected environment and data sensitivity.</li><li><b>Recommend</b> a narrower principal, action, resource, condition, or session boundary.</li></ol></section>
        <section class="content-section"><h2>Example reviewer language</h2>
        <div class="notice"><b>Context-dependent high severity</b><p>The new deployment role can pass <code>prod-reporting-role</code> to Lambda. That target role already grants decryption and read access to the production reporting bucket. Restrict <code>iam:PassRole</code> to the intended runtime role and enforce the expected service through <code>iam:PassedToService</code>.</p></div>
        <p>The important detail is the complete privilege path. A reviewer can confirm or reject the path because the finding names the roles, downstream permission, and proposed condition.</p></section>
        <section class="content-section"><h2>Human and policy gates remain mandatory</h2>
        <p>Use IAM Access Analyzer, organization policies, policy-as-code, and cloud audit data as authoritative inputs. Treat model reasoning as an explainable review layer. Never let the model directly attach policies or approve privileged infrastructure.</p></section>
        """,
        ("IAM policy analysis", "AI IAM security review", "Terraform IAM least privilege", "cross account IAM risk"),
    ),
    Page(
        "context-aware-iac-security/",
        "What Is Context-Aware Infrastructure-as-Code Security Review?",
        "Learn how persistent architecture memory helps IaC security review find cross-resource risks that are invisible in isolated pull-request diffs.",
        "Core concept",
        "Infrastructure risk lives in relationships across files, resources, and reviews.",
        "Context-aware IaC review combines the current diff with a maintained model of architecture, identity, network paths, and prior repository facts.",
        """
        <section class="content-section"><h2>Diff-only review has a structural blind spot</h2>
        <p>A pull request is a useful unit of change, but it is not a complete unit of security meaning. A new route can expose an old workload. A new role trust can activate an old permission. A service account change can connect Kubernetes privilege to cloud privilege. Reviewers reconstruct those relationships manually because the diff does not contain them.</p></section>
        <section class="content-section"><h2>Persistent architecture memory</h2>
        <p>On a cold review, SecReviewAgent parses infrastructure files and builds a repository model containing a summary, components, references, inferred data flows, and IAM relationships. On a warm review, it loads that model, evaluates the change, and updates the stored state when architecture-relevant facts change. This avoids treating every review as a new repository.</p>
        <p>Architecture memory must be governed. It should have provenance, schema versions, freshness controls, encryption, repository boundaries, and deletion behavior. A stale or overbroad memory can create its own security problem.</p></section>
        <section class="content-section"><h2>Layered review is the intended design</h2>
        <div class="layer-stack"><div><b>1. Deterministic scanners</b><span>Known misconfigurations and policy failures</span></div><div><b>2. Architecture context</b><span>Repository relationships, trust paths, and data flows</span></div><div><b>3. Model reasoning</b><span>Specific explanation and remediation</span></div><div><b>4. Human decision</b><span>Validate, suppress, remediate, or approve</span></div></div></section>
        <section class="content-section"><h2>How to measure whether context helps</h2>
        <p>Build a labeled pull-request set with both local and context-dependent issues. Compare deterministic scanners, a no-context model, and the context-aware system on the same set. Report precision, recall, F1, false positives, latency, cost, and reviewer acceptance. Separate cold and warm reviews so architecture reconstruction is not hidden inside one average.</p></section>
        """,
        ("context aware IaC security", "persistent architecture memory", "AI infrastructure code review", "DevSecOps architecture context"),
    ),
    Page(
        "architecture-memory-devsecops/",
        "Persistent Architecture Memory for DevSecOps and AI Code Review",
        "Understand how persistent repository architecture memory supports faster, more contextual DevSecOps security review across pull requests.",
        "Architecture memory",
        "Stop rebuilding the same repository understanding on every review.",
        "Persistent memory can preserve the infrastructure relationships a reviewer needs while keeping raw secrets and unrelated source outside the prompt.",
        """
        <section class="content-section"><h2>What architecture memory should contain</h2>
        <p>A useful representation includes resource inventory, dependency edges, identity relationships, data stores, network boundaries, environment labels, ownership, and selected security notes. It should be compact enough for repeated use and structured enough to update when resources are added, changed, or deleted.</p></section>
        <section class="content-section"><h2>Cold path and warm path</h2>
        <p>The cold path prioritizes IaC files, enforces file and size limits, parses security-relevant structures, summarizes the repository, and stores a versioned context object. The warm path loads that object, applies the pull-request delta, refreshes architecture sections only when needed, and writes the updated version after review.</p>
        <p>This design can reduce repeated parsing and summarization, but teams should measure provider usage and latency rather than assuming savings. Warm-path speed is meaningful only if review quality remains acceptable.</p></section>
        <section class="content-section"><h2>Memory creates responsibilities</h2>
        <ul class="check-list"><li>Encrypt stored context and restrict it to the repository and workload identity.</li><li>Record source hashes and schema version so the reviewer knows what was used.</li><li>Expire or rebuild context after out-of-band infrastructure changes.</li><li>Redact credentials, tokens, passwords, and secret values before persistence.</li><li>Provide a deletion path when a repository or customer leaves the system.</li></ul></section>
        <section class="content-section"><h2>Connection to Secure Context Cache</h2>
        <p>SecReviewAgent is the flagship IaC workflow for the broader <a href="https://krishnamuppidi.github.io/secure-context-cache/">Secure Context Cache</a> architecture. Secure Context Cache adds a policy-scoped release boundary: the reviewer receives only the approved IAM, network, ownership, environment, and dependency facts needed for the task.</p></section>
        """,
        ("persistent architecture memory", "DevSecOps AI memory", "repository context code review", "AI agent memory security"),
    ),
    Page(
        "ai-code-review-vs-static-analysis/",
        "AI Code Review vs Static Analysis for Infrastructure-as-Code",
        "Compare AI-assisted contextual review with static IaC scanners and learn why layered security review produces stronger, more auditable results.",
        "Comparison guide",
        "Static rules and contextual reasoning solve different parts of IaC security.",
        "The strongest workflow keeps deterministic scanners as controls and adds context-aware reasoning where risk crosses resource and file boundaries.",
        """
        <section class="content-section"><h2>What static analysis does well</h2>
        <p>Static IaC scanners are fast, repeatable, and easy to enforce. They excel at known patterns: public storage, missing encryption, unrestricted ingress, privileged containers, weak logging, and violations of organization policy. Their findings can map directly to a rule identifier and a source line.</p></section>
        <section class="content-section"><h2>What an AI review layer can add</h2>
        <p>A model can explain provider semantics, summarize the architecture, connect resources, and propose a remediation that accounts for intent. Persistent repository context can expose a privilege or data path that is not represented in a single rule. The cost is uncertainty: model output must be validated, calibrated, and prevented from taking autonomous action.</p>
        <div class="comparison-grid"><article><h3>Static scanner</h3><ul><li>Deterministic rules</li><li>Low latency</li><li>Clear policy IDs</li><li>Limited architectural inference</li></ul></article><article><h3>SecReviewAgent layer</h3><ul><li>Cross-resource context</li><li>Repository-specific explanation</li><li>Structured remediation</li><li>Requires human validation</li></ul></article></div></section>
        <section class="content-section"><h2>Recommended pipeline</h2>
        <p>Run formatting, validation, and deterministic scanners first. Feed their results plus a bounded architecture view into the contextual reviewer. Deduplicate overlapping findings, preserve the evidence source, and route critical or uncertain findings to an experienced reviewer. Do not hide scanner failures inside a model-generated summary.</p></section>
        <section class="content-section"><h2>Evaluation questions</h2>
        <p>Does the AI layer find context-dependent issues the scanners miss? Does it create more false positives? Does it reduce median human review time? Are recommendations accepted? How much repository content crosses the model boundary? These measures matter more than the raw number of comments.</p></section>
        """,
        ("AI code review vs static analysis", "IaC scanner comparison", "AI DevSecOps security", "static analysis Terraform"),
    ),
    Page(
        "checkov-vs-secreviewagent/",
        "Checkov vs SecReviewAgent: Rules and Context for IaC Security",
        "Compare Checkov policy scanning with SecReviewAgent contextual IaC review and learn how to combine them in a layered pull-request workflow.",
        "Tool comparison",
        "Checkov finds policy violations. SecReviewAgent reasons about repository relationships.",
        "These tools are complementary: one provides deterministic checks, while the other adds bounded architecture context and reviewer-oriented explanation.",
        """
        <section class="content-section"><h2>Different jobs</h2>
        <p>Checkov scans Terraform, Kubernetes, CloudFormation, and other configuration formats against a large library of policies. It is a strong first line for known misconfigurations and compliance rules. SecReviewAgent’s current public parsers focus on Terraform and Kubernetes and add cross-resource context, persistent architecture memory, and structured explanations.</p></section>
        <section class="content-section"><h2>Where Checkov should remain authoritative</h2>
        <p>Use Checkov for deterministic policy IDs, baseline enforcement, suppressions, and supported-framework coverage. A model should not replace a reliable rule with a paraphrased opinion. Preserve the check identifier, file, line, severity, and remediation link in the final review.</p></section>
        <section class="content-section"><h2>Where SecReviewAgent can add value</h2>
        <p>Use the contextual layer when a change must be interpreted against existing IAM relationships, data sensitivity, network boundaries, module behavior, or previous repository knowledge. It can explain why a policy violation matters in this architecture or surface a relationship for which no single Checkov rule exists.</p></section>
        <section class="content-section"><h2>Integration pattern</h2>
        <ol class="number-list"><li>Run Checkov and export machine-readable results.</li><li>Parse the changed Terraform or Kubernetes resources.</li><li>Load the approved repository architecture context.</li><li>Ask SecReviewAgent to reason about unresolved relationships and explain relevant scanner results.</li><li>Deduplicate, retain provenance, and require human approval.</li></ol>
        <div class="notice"><b>No misleading replacement claim</b><p>SecReviewAgent does not claim broader format coverage or deterministic rule depth than Checkov. Its contribution is persistent architectural context for review decisions.</p></div></section>
        """,
        ("Checkov vs AI code review", "Checkov alternative context aware", "Terraform scanner comparison", "IaC security pipeline"),
    ),
    Page(
        "tfsec-vs-secreviewagent/",
        "tfsec vs SecReviewAgent for Terraform Security Review",
        "Compare tfsec-style deterministic Terraform checks with SecReviewAgent architecture-aware review and combine both for pull-request security.",
        "Tool comparison",
        "Fast Terraform checks first. Repository-aware reasoning second.",
        "tfsec and related Trivy configuration checks detect known Terraform risks; SecReviewAgent is designed for relationships that require stored architecture context.",
        """
        <section class="content-section"><h2>Deterministic Terraform scanning</h2>
        <p>tfsec became a familiar choice because it maps Terraform configuration to concrete security checks with fast local and CI execution. Today many teams consume that capability through Trivy configuration scanning. This remains a strong control for known insecure values and resource patterns.</p></section>
        <section class="content-section"><h2>Context-aware review</h2>
        <p>SecReviewAgent parses Terraform resources and references, builds an architecture view, and asks how the pull request changes existing trust, network, or data paths. A new route, role, or attachment can be risky because of resources that were not edited. This is the gap persistent memory is intended to address.</p></section>
        <section class="content-section"><h2>Use both without creating noise</h2>
        <p>Start with deterministic results. Mark them as scanner evidence. Run contextual reasoning only on security-relevant deltas and the minimum approved architecture facts. Merge exact duplicates, but do not let a model suppress a scanner failure silently. Route uncertain relationship findings to a human with the relevant resource graph.</p></section>
        <section class="content-section"><h2>Selection guide</h2>
        <ul class="check-list"><li>Need fast known checks in every commit? Use deterministic scanning.</li><li>Need custom organization policy? Add policy-as-code.</li><li>Need a cross-file trust or data-path explanation? Add context-aware review.</li><li>Need merge enforcement? Base it on validated rules and explicit human decisions.</li><li>Need evidence of improvement? Evaluate all paths on the same labeled PR set.</li></ul></section>
        """,
        ("tfsec vs AI review", "tfsec alternative context", "Terraform security scanner AI", "Trivy config AI review"),
    ),
    Page(
        "secure-ai-code-review/",
        "Secure AI Code Review: Least-Privilege Context for IaC",
        "Design AI-assisted code review with least-privilege repository context, secret redaction, provenance, audit records, and human approval.",
        "Secure AI review",
        "The model should receive the minimum approved context—not the entire enterprise map.",
        "Security review can create a new data-exposure path if repository context, secrets, and architecture memory are not governed before model invocation.",
        """
        <section class="content-section"><h2>Bound the context before inference</h2>
        <p>Changed files alone may be insufficient, but whole-repository prompts are not the only alternative. Select the IAM, network, data, ownership, and dependency facts required for the review. Deny unrelated repositories, secret-adjacent content, and broad topology. Record why each slice was released.</p></section>
        <section class="content-section"><h2>Minimum controls</h2>
        <ul class="check-list"><li>Workload authentication and repository-scoped authorization.</li><li>Secret, credential, token, and sensitive-literal redaction.</li><li>Encrypted context storage with schema and freshness metadata.</li><li>Source hashes, selected facts, denied facts, and model version in the audit record.</li><li>Human approval for merge, policy exceptions, and production actions.</li><li>Retention and deletion controls for repository memory and prompts.</li></ul></section>
        <section class="content-section"><h2>Fail closed on missing authorization</h2>
        <p>If the reviewer cannot obtain an approved context set, it should stop or fall back to an explicitly limited diff-only review. It should not silently query broad stores or reuse context from another repository, tenant, or environment.</p></section>
        <section class="content-section"><h2>Measure security and quality together</h2>
        <p>Track prohibited-context release, required-fact coverage, finding precision and recall, reviewer acceptance, latency, and token usage. A cheaper prompt is not an improvement if it misses a required security fact. A higher recall is not acceptable if it exposes unauthorized repository content.</p>
        <p>SecReviewAgent can use <a href="https://krishnamuppidi.github.io/secure-context-cache/">Secure Context Cache</a> as the context-release layer for this design.</p></section>
        """,
        ("secure AI code review", "least privilege LLM context", "AI code review privacy", "secure IaC AI"),
    ),
    Page(
        "iac-security-review-checklist/",
        "Infrastructure-as-Code Security Review Checklist",
        "Use this practical IaC security review checklist for Terraform, Kubernetes, IAM, networking, secrets, provenance, and AI-assisted review.",
        "Practical checklist",
        "A reviewer-ready checklist for infrastructure pull requests.",
        "Use deterministic controls first, then evaluate architecture relationships, deployment impact, and the evidence behind any AI-generated finding.",
        """
        <section class="content-section"><h2>Identity and access</h2><ul class="check-list"><li>Are actions, resources, principals, and trust conditions narrowly scoped?</li><li>Can any identity pass or assume a more privileged role?</li><li>Do workload identities match the intended namespace, service, account, and environment?</li><li>Are policy exceptions explicit, time-bounded, and owned?</li></ul></section>
        <section class="content-section"><h2>Network and data paths</h2><ul class="check-list"><li>Does ingress expose public or administrative ports?</li><li>Is egress constrained for sensitive workloads?</li><li>Do routes, endpoints, load balancers, and security groups preserve segmentation?</li><li>Are storage, database, and key-management resources encrypted and access-scoped?</li></ul></section>
        <section class="content-section"><h2>Kubernetes and containers</h2><ul class="check-list"><li>Are privileged mode, host namespaces, host paths, and unsafe capabilities disabled?</li><li>Are RBAC bindings namespaced and verb/resource scopes minimal?</li><li>Do NetworkPolicies cover both ingress and egress where required?</li><li>Are images pinned, scanned, and promoted with verifiable provenance?</li></ul></section>
        <section class="content-section"><h2>AI-assisted review controls</h2><ul class="check-list"><li>Was the context authorized for this repository and task?</li><li>Were secrets and sensitive literals removed before inference?</li><li>Does every finding cite a resource and configuration value?</li><li>Are deterministic scanner results distinguishable from model reasoning?</li><li>Is a human responsible for the final merge or exception decision?</li></ul></section>
        <section class="content-section"><h2>Evidence to retain</h2><p>Preserve the pull-request commit, scanner versions, policy bundle, selected context version, model and prompt version, structured findings, reviewer disposition, remediation commit, and final approval. This turns review from a comment stream into auditable engineering evidence.</p></section>
        """,
        ("IaC security review checklist", "Terraform review checklist", "Kubernetes security checklist", "DevSecOps pull request checklist"),
    ),
    Page(
        "research/",
        "SecReviewAgent Research, Evaluation Method, and Claim Boundaries",
        "Read the SecReviewAgent research summary, ICUFN presentation status, evaluation design, reported results, limitations, and reproducibility boundaries.",
        "Research",
        "Persistent architecture memory, evaluated as a review mechanism.",
        "The SecReviewAgent paper was accepted and presented at ICUFN 2026. This page separates paper-reported results from guarantees about the public prototype.",
        """
        <section class="content-section"><h2>Research contribution</h2>
        <p>The paper, <em>SecReviewAgent: Context-Aware Security Review of Infrastructure-as-Code Using Persistent Architecture Memory</em>, presents a repository memory design, cold and warm review algorithms, Terraform and Kubernetes parsing, structured findings, and an empirical comparison focused on context-dependent security issues.</p>
        <p>The work was accepted and presented at the 2026 International Conference on Ubiquitous and Future Networks (ICUFN). The conference manuscript names Naga Krishna Reddy Muppidi, Veera Ravindra Divi, Sneha Gullapalli, and Rambabu Pasumarthy as authors.</p></section>
        <section class="content-section"><h2>Results reported in the paper</h2>
        <div class="metric-grid"><div><strong>847</strong><span>IaC pull requests</span></div><div><strong>23</strong><span>repositories</span></div><div><strong>0.89</strong><span>precision</span></div><div><strong>0.83</strong><span>F1</span></div><div><strong>2.4×</strong><span>context-dependent recall vs no-context baseline</span></div><div><strong>73%</strong><span>warm-review latency reduction</span></div></div>
        <p class="fine-print">These are manuscript-reported research results under the paper’s dataset, labeling process, baselines, and implementation. They are not universal production guarantees.</p></section>
        <section class="content-section"><h2>Evaluation design</h2>
        <p>The manuscript describes comparisons with deterministic scanners and a no-context model, dual security labeling with adjudication, separate context-dependent recall analysis, cold and warm latency measurement, and a controlled practitioner study. The design is intended to test the specific mechanism: whether persistent repository context improves review of relational infrastructure risks.</p></section>
        <section class="content-section"><h2>Limitations and reproducibility</h2>
        <p>Private repositories cannot be redistributed. Aggregate statistics and methodology do not substitute for a public benchmark corpus. Model behavior, prompt design, parser quality, and baseline configuration can affect results. Architecture memory can become stale. Cross-repository systems are only partially modeled. Human review remains necessary.</p>
        <p><a class="button button-primary" href="../assets/secreviewagent-icufn-2026-paper.pdf" data-track="paper_download">Read the conference manuscript</a></p></section>
        """,
        ("SecReviewAgent research paper", "persistent memory IaC research", "LLM security review evaluation", "ICUFN 2026 SecReviewAgent"),
    ),
    Page(
        "about/",
        "About SecReviewAgent and Naga Krishna Reddy Muppidi",
        "Learn about SecReviewAgent, its independent research origin, open-source implementation, product family, and author Naga Krishna Reddy Muppidi.",
        "About",
        "An independent research and open-source project for context-aware IaC security review.",
        "SecReviewAgent turns repository architecture context into specific, reviewer-ready explanations for Terraform and Kubernetes changes.",
        """
        <section class="content-section"><h2>Why this project exists</h2>
        <p>Infrastructure code encodes identity, networking, storage, encryption, and deployment authority, but pull requests show only the lines that changed. SecReviewAgent was created to preserve the architecture relationships a reviewer repeatedly reconstructs and use them to interpret the security impact of later changes.</p></section>
        <section class="content-section"><h2>Author</h2>
        <p>I am Naga Krishna Reddy Muppidi, an independent researcher and senior platform and cloud infrastructure engineer with more than ten years of experience across cloud platforms, Kubernetes, infrastructure automation, cybersecurity, distributed systems, FinOps, and regulated enterprise environments. My research focuses on secure AI agents, cloud security, cost-aware infrastructure, governance, and reliable AI-assisted operations.</p>
        <p><a href="https://scholar.google.com/citations?user=IKcQzPkAAAAJ&amp;hl=en">Google Scholar</a> · <a href="https://orcid.org/0009-0001-4342-540X">ORCID</a> · <a href="https://www.linkedin.com/in/krishna-reddy-4b11ab133">LinkedIn</a> · <a href="https://github.com/krishnamuppidi">GitHub</a></p></section>
        <section class="content-section"><h2>Product family</h2>
        <p>SecReviewAgent is the flagship Infrastructure-as-Code workflow. <a href="https://krishnamuppidi.github.io/secure-context-cache/">Secure Context Cache</a> is the broader framework for selecting, reusing, authorizing, and measuring task context. Agent Context Gateway is the runtime boundary that can authenticate a workload and release a policy-scoped context capsule before model invocation.</p></section>
        <section class="content-section"><h2>Open-source boundary</h2>
        <p>The public repository is an inspectable reference implementation released under the MIT License. It is not a managed security service and does not represent a certification, warranty, or replacement for experienced human review. Organizations should validate it on authorized data and their own threat model.</p></section>
        """,
        ("Naga Krishna Reddy Muppidi SecReviewAgent", "SecReviewAgent author", "IaC AI researcher", "cloud security research"),
    ),
)


def nav(prefix: str) -> str:
    return f"""
    <nav class="nav" aria-label="Primary navigation">
      <div class="container nav-inner">
        <a class="brand" href="{prefix}" aria-label="SecReviewAgent home"><span class="brand-mark">S<span>R</span></span><span>SecReviewAgent</span></a>
        <button class="menu-button" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Open navigation"><span></span><span></span><span></span></button>
        <div class="nav-links" id="nav-links"><a href="{prefix}#how-it-works">How it works</a><a href="{prefix}use-cases/">Use cases</a><a href="{prefix}examples/">Examples</a><a href="{prefix}research/">Research</a><a href="{prefix}docs/">Docs</a></div>
        <a class="button button-small nav-cta" href="{REPOSITORY}">View GitHub <span aria-hidden="true">↗</span></a>
      </div>
    </nav>"""


def footer(prefix: str) -> str:
    return f"""
    <footer class="footer"><div class="container footer-grid"><div><a class="brand" href="{prefix}"><span class="brand-mark">S<span>R</span></span><span>SecReviewAgent</span></a><p>Context-aware security review for Infrastructure-as-Code.</p></div><div><b>Explore</b><a href="{prefix}use-cases/">Use cases</a><a href="{prefix}examples/">Examples</a><a href="{prefix}research/">Research</a><a href="{prefix}docs/">Documentation</a></div><div><b>Guides</b><a href="{prefix}terraform-security-review/">Terraform review</a><a href="{prefix}kubernetes-security-review/">Kubernetes review</a><a href="{prefix}iac-security-review-checklist/">IaC checklist</a><a href="{prefix}about/">About</a></div><div><b>Project</b><a href="{REPOSITORY}">Source code</a><a href="{prefix}assets/secreviewagent-icufn-2026-paper.pdf">Research paper</a><button id="analytics-preferences" class="footer-button" type="button">Analytics preferences</button></div></div><div class="container footer-bottom"><span>© <span id="year">2026</span> {AUTHOR}. MIT-licensed reference implementation.</span><span>Independent research · Human review required</span></div></footer>
    <div id="analytics-consent" class="consent" role="dialog" aria-labelledby="analytics-consent-title" hidden><div><b id="analytics-consent-title">Privacy-respecting analytics</b><p>Allow anonymous GA4 usage analytics to improve the site. Advertising, Google Signals, personalization, names, emails, form contents, query strings, and full outbound URLs are not sent.</p></div><div class="consent-actions"><button class="button button-ghost" type="button" data-analytics-choice="denied">Decline</button><button class="button button-primary" type="button" data-analytics-choice="granted">Allow analytics</button></div></div>"""


def head(title: str, description: str, canonical: str, keywords: tuple[str, ...], prefix: str, schema: dict) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#070b18" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}" />
  <meta name="keywords" content="{html.escape(', '.join(keywords), quote=True)}" />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <link rel="canonical" href="{canonical}" />
  <link rel="alternate" type="text/markdown" href="index.md" />
  <meta property="og:title" content="{html.escape(title, quote=True)}" />
  <meta property="og:description" content="{html.escape(description, quote=True)}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:site_name" content="SecReviewAgent" />
  <meta property="og:image" content="{BASE_URL}assets/secreviewagent-social-preview.png" />
  <meta property="og:image:alt" content="SecReviewAgent context-aware Infrastructure-as-Code security review" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{html.escape(title, quote=True)}" />
  <meta name="twitter:description" content="{html.escape(description, quote=True)}" />
  <meta name="twitter:image" content="{BASE_URL}assets/secreviewagent-social-preview.png" />
  <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="{prefix}styles.css" />
  <script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script>
  <script defer src="{prefix}analytics.js"></script>
  <script defer src="{prefix}app.js"></script>
</head>"""


def schema_for(page: Page, canonical: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page.title,
        "description": page.description,
        "url": canonical,
        "dateModified": TODAY,
        "author": {
            "@type": "Person",
            "name": AUTHOR,
            "url": "https://scholar.google.com/citations?user=IKcQzPkAAAAJ&hl=en",
        },
        "publisher": {"@type": "Person", "name": AUTHOR},
        "isPartOf": {"@type": "WebSite", "name": "SecReviewAgent", "url": BASE_URL},
    }


def render_page(page: Page) -> str:
    canonical = BASE_URL + page.route
    prefix = "../" * len(Path(page.route).parts)
    return f"""{head(page.title, page.description, canonical, page.keywords, prefix, schema_for(page, canonical))}
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  {nav(prefix)}
  <main id="main">
    <header class="page-hero"><div class="page-grid"></div><div class="container narrow reveal"><span class="eyebrow">{page.eyebrow}</span><h1>{page.heading}</h1><p>{page.lead}</p><div class="breadcrumb"><a href="{prefix}">SecReviewAgent</a><span>/</span><span>{page.eyebrow}</span></div></div></header>
    <article class="article container narrow reveal">{page.body}</article>
    <section class="related"><div class="container narrow"><span class="eyebrow">Continue exploring</span><h2>Put context-aware review into practice.</h2><div class="related-links"><a href="{prefix}examples/">Worked examples <span>→</span></a><a href="{prefix}docs/">Documentation <span>→</span></a><a href="{prefix}research/">Research and evidence <span>→</span></a></div></div></section>
  </main>
  {footer(prefix)}
</body>
</html>"""


HOME_TITLE = "SecReviewAgent — Context-Aware Security Review for Infrastructure-as-Code"
HOME_DESCRIPTION = "Review Terraform and Kubernetes changes with persistent architecture memory, structured findings, and explainable security context."


def homepage() -> str:
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "name": "SecReviewAgent",
                "applicationCategory": "SecurityApplication",
                "operatingSystem": "Cross-platform",
                "description": HOME_DESCRIPTION,
                "url": BASE_URL,
                "codeRepository": REPOSITORY,
                "license": "https://opensource.org/license/mit",
                "author": {"@type": "Person", "name": AUTHOR},
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            {"@type": "WebSite", "name": "SecReviewAgent", "url": BASE_URL},
        ],
    }
    return f"""{head(HOME_TITLE, HOME_DESCRIPTION, BASE_URL, ("IaC security review", "AI Terraform review", "Kubernetes security review", "persistent architecture memory"), "", schema)}
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  {nav("")}
  <main id="main">
    <header class="hero" id="top">
      <div class="hero-grid"></div><div class="hero-orb orb-one"></div><div class="hero-orb orb-two"></div>
      <div class="container hero-layout">
        <div class="hero-copy reveal">
          <a class="release-pill" href="{REPOSITORY}"><span class="status-dot"></span>Open-source IaC security research · MIT <span>↗</span></a>
          <h1>Security review that remembers<br /><span>the architecture.</span></h1>
          <p class="hero-lead">SecReviewAgent reviews Terraform and Kubernetes changes against persistent repository context—so IAM paths, network boundaries, workload identity, and data relationships are not lost between pull requests.</p>
          <div class="hero-actions"><a class="button button-primary" href="examples/">Explore worked examples</a><a class="button button-ghost" href="docs/">Run the prototype <span>→</span></a></div>
          <div class="hero-proof"><span><i>✓</i> Terraform + Kubernetes</span><span><i>✓</i> Structured findings</span><span><i>✓</i> Human approval stays in control</span></div>
        </div>
        <div class="review-console reveal reveal-delay" aria-label="Context-aware review preview">
          <div class="console-top"><span class="window-dots"><i></i><i></i><i></i></span><code>PR #184 · terraform/prod</code><span class="console-live"><i></i>context loaded</span></div>
          <div class="console-body">
            <div class="diff"><span class="line">+ Action = "s3:GetObject"</span><span class="line">+ Resource = aws_s3_bucket.risk_data.arn</span></div>
            <div class="context-path"><div><small>Changed permission</small><b>reporting-reader</b></div><i>→</i><div><small>Existing trust</small><b>external-ci-role</b></div><i>→</i><div><small>Data boundary</small><b>prod-risk-data/*</b></div></div>
            <div class="finding"><span>HIGH · context-dependent</span><h3>Cross-account read path reaches production risk data.</h3><p>The new permission combines with an existing trust policy not visible in the changed file.</p><div><code>Restrict principal + prefix + external ID</code></div></div>
          </div>
        </div>
      </div>
      <div class="container capability-strip"><span>Built for</span><b>Terraform</b><b>Kubernetes</b><b>IAM</b><b>RBAC</b><b>Network policy</b><b>Pull requests</b><b>DevSecOps</b></div>
    </header>

    <section class="section" id="why-context"><div class="container">
      <div class="section-heading reveal"><span class="eyebrow">The missing review layer</span><h2>A safe-looking line can create<br /><span>an unsafe architecture path.</span></h2><p>Deterministic scanners catch known patterns. SecReviewAgent adds the repository relationships required to explain how a change affects the system around it.</p></div>
      <div class="bento-grid">
        <article class="bento bento-large reveal"><span class="card-index">01 · Persistent context</span><h3>Carry architecture knowledge across pull requests.</h3><p>Build a versioned view of resources, references, IAM relationships, data paths, and security notes once, then update it as the repository changes.</p><div class="memory-map"><span>Resources</span><span>IAM graph</span><span>Network</span><span>Data paths</span><span>Ownership</span></div></article>
        <article class="bento reveal"><span class="card-index">02 · Specific evidence</span><h3>Explain the actual configuration.</h3><p>Findings name resource addresses, configuration values, affected relationships, and a concrete remediation.</p></article>
        <article class="bento reveal"><span class="card-index">03 · Layered security</span><h3>Complement scanners. Do not hide them.</h3><p>Keep Checkov, tfsec/Trivy, OPA, and human review. Add contextual reasoning where rules cannot see the full path.</p></article>
        <article class="bento bento-wide reveal"><span class="card-index">04 · Controlled boundary</span><h3>Release only the context approved for the review task.</h3><p>Pair SecReviewAgent with Secure Context Cache to minimize prompt scope, preserve provenance, and deny unrelated repository knowledge.</p><a href="secure-ai-code-review/">Explore secure AI review controls →</a></article>
      </div>
    </div></section>

    <section class="section process-section" id="how-it-works"><div class="container">
      <div class="section-heading reveal"><span class="eyrow eyebrow">Review flow</span><h2>Cold-start once. Review in context.<br /><span>Update memory deliberately.</span></h2></div>
      <div class="steps"><article><span>01</span><h3>Parse</h3><p>Extract Terraform or Kubernetes resources, policies, bindings, and references.</p></article><article><span>02</span><h3>Build or load</h3><p>Create repository context on the first review; load the versioned architecture view later.</p></article><article><span>03</span><h3>Reason</h3><p>Evaluate the diff beside approved architecture facts and return strict structured findings.</p></article><article><span>04</span><h3>Decide</h3><p>A human validates the evidence, remediates, suppresses, or approves. The model never merges.</p></article></div>
      <div class="center-action"><a class="button button-primary" href="context-aware-iac-security/">Learn the architecture</a></div>
    </div></section>

    <section class="section evidence-section"><div class="container evidence-layout">
      <div class="reveal"><span class="eyebrow">Peer-reviewed research</span><h2>Evaluated on context-dependent IaC findings.</h2><p>The SecReviewAgent manuscript was accepted and presented at ICUFN 2026. It reports a labeled-corpus evaluation and practitioner study designed to test the effect of persistent architecture memory.</p><a class="button button-ghost" href="research/">Read results and limitations</a></div>
      <div class="metric-grid reveal"><div><strong>847</strong><span>pull requests</span></div><div><strong>23</strong><span>repositories</span></div><div><strong>0.89</strong><span>precision</span></div><div><strong>0.83</strong><span>F1</span></div><div><strong>2.4×</strong><span>context recall</span></div><div><strong>73%</strong><span>warm latency reduction</span></div><p class="metric-note">Paper-reported research results; not universal production guarantees.</p></div>
    </div></section>

    <section class="section"><div class="container">
      <div class="section-heading reveal"><span class="eyebrow">Practical coverage</span><h2>Start with supported workflows.<br /><span>Expand through tested adapters.</span></h2></div>
      <div class="use-grid"><a href="terraform-security-review/"><span>Terraform</span><h3>Resource, IAM, security-group, and reference analysis</h3><p>Trace a change through existing infrastructure relationships.</p><b>Explore →</b></a><a href="kubernetes-security-review/"><span>Kubernetes</span><h3>Workload, RBAC, IRSA, ingress, and network policy</h3><p>Connect cluster privilege to workload and cloud identity.</p><b>Explore →</b></a><a href="iam-policy-analysis/"><span>IAM</span><h3>Actions, resources, principals, and trust paths</h3><p>Review least privilege in architectural context.</p><b>Explore →</b></a><a href="examples/"><span>Examples</span><h3>Reviewer-ready findings with actual configuration</h3><p>See the changed line, stored context, and remediation together.</p><b>Explore →</b></a></div>
    </div></section>

    <section class="section search-hub"><div class="container">
      <div class="section-heading reveal"><span class="eyebrow">Technical learning hub</span><h2>Detailed guides, not thin keyword pages.</h2><p>Each resource answers a distinct engineering question and links back to runnable code or an explicit roadmap boundary.</p></div>
      <div class="guide-list reveal"><a href="ai-code-review-vs-static-analysis/"><span>Comparison</span><b>AI code review vs static analysis for IaC</b><i>→</i></a><a href="checkov-vs-secreviewagent/"><span>Comparison</span><b>Checkov vs SecReviewAgent</b><i>→</i></a><a href="tfsec-vs-secreviewagent/"><span>Comparison</span><b>tfsec vs SecReviewAgent</b><i>→</i></a><a href="architecture-memory-devsecops/"><span>Architecture</span><b>Persistent repository memory for DevSecOps</b><i>→</i></a><a href="secure-ai-code-review/"><span>Security</span><b>Least-privilege context for AI code review</b><i>→</i></a><a href="iac-security-review-checklist/"><span>Checklist</span><b>Infrastructure-as-Code review checklist</b><i>→</i></a></div>
    </div></section>

    <section class="cta-section"><div class="container cta-card reveal"><div><span class="eyebrow">Inspect the implementation</span><h2>Run the prototype on an authorized test repository.</h2><p>Start with the included fixture, verify the structured output, and evaluate against a labeled pull-request set before production use.</p></div><div><a class="button button-primary" href="docs/">Open documentation</a><a class="button button-ghost" href="{REPOSITORY}">View source ↗</a></div></div></section>
  </main>
  {footer("")}
</body>
</html>"""


def markdown_for(page: Page) -> str:
    text = re.sub(r"<pre><code>(.*?)</code></pre>", lambda match: f"\n```\n{html.unescape(match.group(1))}\n```\n", page.body, flags=re.S)
    text = re.sub(r"<a [^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", lambda match: f"[{re.sub('<[^>]+>', '', match.group(2)).strip()}]({match.group(1)})", text, flags=re.S)
    text = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", text, flags=re.S)
    text = re.sub(r"<h3>(.*?)</h3>", r"\n### \1\n", text, flags=re.S)
    text = re.sub(r"<li>(.*?)</li>", r"- \1\n", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</p>|</div>|</article>|</section>|</ol>|</ul>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return f"# {page.title}\n\nCanonical URL: {BASE_URL}{page.route}\nSource code: {REPOSITORY}\n\n{page.lead}\n\n{text}\n"


def home_markdown() -> str:
    links = "\n".join(f"- [{page.title}]({BASE_URL}{page.route}index.md)" for page in PAGES)
    return f"""# SecReviewAgent

Canonical URL: {BASE_URL}
Source code: {REPOSITORY}

SecReviewAgent is an open-source, context-aware security review system for Terraform and Kubernetes. It preserves repository architecture memory across pull requests and returns structured, reviewer-ready findings.

## Capabilities

- Terraform resource, reference, IAM policy, and security-group parsing.
- Kubernetes workload, RBAC, service-account, IRSA, ingress, and NetworkPolicy parsing.
- Pull-request diff analysis with architecture context.
- Structured findings with affected resources and actionable recommendations.
- AWS serverless webhook reference deployment.
- Human approval remains required.

## Research boundary

The SecReviewAgent paper was accepted and presented at ICUFN 2026. Its reported evaluation results are research results under the manuscript's dataset and method, not universal production guarantees.

## Guides

{links}
"""


def write_discovery(urls: list[str]) -> None:
    sitemap_entries = "\n".join(
        f"""  <url><loc>{url}</loc><lastmod>{TODAY}</lastmod><changefreq>{'weekly' if url == BASE_URL else 'monthly'}</changefreq><priority>{'1.0' if url == BASE_URL else '0.8'}</priority></url>"""
        for url in urls
    )
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_entries}\n</urlset>\n'
    )
    (SITE / "sitemap.txt").write_text("\n".join(urls) + "\n")
    (SITE / "robots.txt").write_text(
        """# Search and answer-engine crawlers
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: *
Allow: /

Sitemap: https://krishnamuppidi.github.io/secreviewagent-ai/sitemap.xml
Sitemap: https://krishnamuppidi.github.io/secreviewagent-ai/sitemap.txt
"""
    )
    guide_lines = "\n".join(f"- [{page.title}]({BASE_URL}{page.route}index.md)" for page in PAGES)
    (SITE / "llms.txt").write_text(
        f"""# SecReviewAgent

> Context-aware Infrastructure-as-Code security review using persistent architecture memory.

Canonical terminology: SecReviewAgent is the flagship IaC security review application. Secure Context Cache is the broader context-selection and authorization framework. Agent Context Gateway is the runtime context-release boundary.

Claim boundary: the public implementation supports Terraform and Kubernetes parsing, structured review, PR diffs, a webhook, and an AWS deployment template. CloudFormation, Pulumi, Helm, Kustomize, CI pipeline, OPA/Rego, Dockerfile, and SBOM adapters are roadmap items unless a guide explicitly describes a render-and-review integration. Manuscript-reported metrics are research results, not universal production guarantees.

## Start here

- [Product website]({BASE_URL})
- [Documentation]({BASE_URL}docs/index.md)
- [Use cases]({BASE_URL}use-cases/index.md)
- [Worked examples]({BASE_URL}examples/index.md)
- [Research and limitations]({BASE_URL}research/index.md)
- [GitHub repository]({REPOSITORY})

## Technical guides

{guide_lines}
"""
    )
    full = [home_markdown()]
    for page in PAGES:
        full.append(markdown_for(page))
    (SITE / "llms-full.txt").write_text("\n\n---\n\n".join(full))
    payload = {
        "host": "krishnamuppidi.github.io",
        "key": "5147a31f7511eb481f0b18ac0488bd55",
        "keyLocation": f"{BASE_URL}5147a31f7511eb481f0b18ac0488bd55.txt",
        "urlList": urls,
    }
    (SITE / "indexnow-urls.json").write_text(json.dumps(payload, indent=2) + "\n")
    (SITE / "5147a31f7511eb481f0b18ac0488bd55.txt").write_text(payload["key"] + "\n")


def main() -> None:
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(homepage())
    (SITE / "index.md").write_text(home_markdown())
    urls = [BASE_URL]
    for page in PAGES:
        directory = SITE / page.route
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(render_page(page))
        (directory / "index.md").write_text(markdown_for(page))
        urls.append(BASE_URL + page.route)
    write_discovery(urls)
    print(f"Built {len(urls)} pages in {SITE}")


if __name__ == "__main__":
    main()
