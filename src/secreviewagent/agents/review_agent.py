"""
SecReviewAgent - Educational IaC Security Review Agent.

The main agent that:
1. Parses IaC (Terraform/K8s) to extract actual resource configs
2. Sends ONLY what's found to the LLM for dynamic understanding
3. LLM explains services based on actual config, not static knowledge base
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

import anthropic

from secreviewagent.parsers.terraform import TerraformParser
from secreviewagent.parsers.kubernetes import KubernetesParser


@dataclass
class SecurityFinding:
    """A security finding with educational context."""
    
    severity: str  # critical, high, medium, low, info
    title: str
    description: str
    affected_resources: list[str]
    recommendation: str
    concept_references: list[str] = field(default_factory=list)


@dataclass
class ReviewResult:
    """Complete review result."""
    
    architecture_summary: str
    service_interactions: list[dict]
    security_findings: list[SecurityFinding]
    service_explanations: dict[str, str]  # Dynamic explanations from LLM
    raw_resources: dict


class SecReviewAgent:
    """
    Educational IaC Security Review Agent.
    
    Analyzes Infrastructure-as-Code and generates educational security reviews.
    
    KEY DESIGN: No static knowledge base. The LLM reads the actual Terraform/K8s
    config and explains what each resource does based on its actual configuration.
    This is more accurate and works for ANY provider without pre-built knowledge.
    """
    
    SYSTEM_PROMPT = """You are SecReviewAgent, an educational security review assistant for Infrastructure-as-Code.

Your audience is security practitioners who may not be deeply familiar with AWS, EKS, or cloud-native architectures.

CRITICAL: You will receive the ACTUAL resource configurations from the Terraform/Kubernetes files. 
Do NOT rely on generic knowledge - explain what THIS SPECIFIC configuration does based on the actual values you see.

Your job is to:
1. **Explain what each resource ACTUALLY does** based on its configuration (not generic docs)
2. **Identify security concerns** with severity ratings
3. **Teach cloud concepts** inline when relevant (explain acronyms, use analogies)
4. **Provide actionable recommendations** that explain the "why"

TONE:
- Educational and friendly, not alarming
- Explain acronyms and cloud jargon inline
- Use analogies to make concepts accessible
- Be SPECIFIC - reference actual values from the config

OUTPUT FORMAT:
Respond with a JSON object containing:
{
  "architecture_summary": "Plain English description of what this infrastructure creates - reference specific resource names",
  "service_explanations": {
    "resource_address": "What this specific resource does, based on its actual config. Include what the service type is and why these specific settings matter."
  },
  "service_interactions": [
    {
      "from": "resource address",
      "to": "resource address", 
      "interaction": "what happens between them",
      "permissions": "what permissions enable this (reference actual IAM policy if present)"
    }
  ],
  "security_findings": [
    {
      "severity": "critical|high|medium|low|info",
      "title": "Short title",
      "description": "Detailed explanation - reference specific config values that cause this issue",
      "affected_resources": ["actual.resource.addresses"],
      "recommendation": "What to change and why",
      "concepts": ["security concepts this relates to"]
    }
  ]
}"""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
    ):
        """
        Initialize the review agent.
        
        Args:
            model: Anthropic model to use
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.model = model
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        
        self.tf_parser = TerraformParser()
        self.k8s_parser = KubernetesParser()
    
    def review_terraform_directory(self, directory: str) -> ReviewResult:
        """
        Review a directory of Terraform files.
        
        Args:
            directory: Path to Terraform directory
        
        Returns:
            ReviewResult with analysis
        """
        # Parse Terraform - get actual resource configs
        self.tf_parser.parse_directory(directory)
        
        # Get the raw parsed data with ACTUAL configurations
        parsed_data = self._get_terraform_context()
        
        # Call LLM with actual configs - no static knowledge base
        llm_analysis = self._analyze_with_llm(parsed_data, "terraform")
        
        return self._build_result(llm_analysis, parsed_data)
    
    def _get_terraform_context(self) -> dict:
        """
        Extract actual Terraform resource configurations for LLM analysis.
        
        Returns full resource configs, not just metadata - so LLM can understand
        what each resource ACTUALLY does based on its real settings.
        """
        context = {
            "resources": {},
            "iam_policies": {},
            "security_groups": {},
        }
        
        # Include FULL resource configs, not just summaries
        for addr, resource in self.tf_parser.resources.items():
            context["resources"][addr] = {
                "type": resource.resource_type,
                "name": resource.name,
                "config": resource.attributes,  # Actual config values!
                "references": resource.references,
            }
        
        # Include actual IAM policy statements
        for addr, policy in self.tf_parser.iam_policies.items():
            context["iam_policies"][addr] = {
                "name": policy.name,
                "statements": policy.statements,  # Actual policy!
                "allowed_actions": policy.get_allowed_actions(),
                "allowed_resources": policy.get_allowed_resources(),
            }
        
        # Include actual security group rules
        for addr, rules in self.tf_parser.security_groups.items():
            context["security_groups"][addr] = [
                {
                    "direction": r.direction,
                    "protocol": r.protocol,
                    "from_port": r.from_port,
                    "to_port": r.to_port,
                    "cidr_blocks": r.cidr_blocks,
                    "is_public": r.is_public,
                    "description": r.description,
                }
                for r in rules
            ]
        
        return context
    
    def review_kubernetes_directory(self, directory: str) -> ReviewResult:
        """Review a directory of Kubernetes manifests."""
        self.k8s_parser.parse_directory(directory)
        parsed_data = self._get_kubernetes_context()
        llm_analysis = self._analyze_with_llm(parsed_data, "kubernetes")
        return self._build_result(llm_analysis, parsed_data)
    
    def _get_kubernetes_context(self) -> dict:
        """Extract actual K8s resource configurations."""
        context = {
            "resources": {},
            "rbac_bindings": [],
            "network_policies": [],
            "service_account_roles": self.k8s_parser.service_account_roles,
        }
        
        for addr, resource in self.k8s_parser.resources.items():
            context["resources"][addr] = {
                "kind": resource.kind,
                "name": resource.name,
                "namespace": resource.namespace,
                "spec": resource.spec,  # Actual spec!
                "annotations": resource.annotations,
                "irsa_role_arn": resource.irsa_role_arn,
            }
        
        for binding in self.k8s_parser.rbac_bindings:
            context["rbac_bindings"].append({
                "subject": f"{binding.subject_kind}/{binding.subject_namespace or 'cluster'}/{binding.subject_name}",
                "role": f"{binding.role_kind}/{binding.role_name}",
                "binding": binding.binding_name,
            })
        
        for policy in self.k8s_parser.network_policies:
            context["network_policies"].append({
                "policy": policy.policy_name,
                "direction": policy.direction,
                "pod_selector": policy.pod_selector,
                "peer_selector": policy.peer_selector,
                "namespace_selector": policy.namespace_selector,
                "ip_block": policy.ip_block,
                "ports": policy.ports,
            })
        
        return context
    
    def review_pr_diff(self, diff: str, file_type: str = "terraform") -> ReviewResult:
        """Review a PR diff."""
        if file_type == "terraform":
            changes = self.tf_parser.parse_diff(diff)
        else:
            changes = {"added": [], "removed": [], "modified": []}
        
        context = {
            "diff_type": file_type,
            "changes": changes,
            "raw_diff": diff[:8000],  # Include more context
        }
        
        llm_analysis = self._analyze_diff_with_llm(context)
        return self._build_result(llm_analysis, {"changes": changes})
    
    def _analyze_with_llm(self, parsed_data: dict, iac_type: str) -> dict:
        """
        Call LLM to analyze the infrastructure.
        
        The LLM receives ACTUAL resource configurations and must explain
        based on what it sees - no static knowledge base needed.
        """
        
        # Serialize with actual configs
        config_json = json.dumps(parsed_data, indent=2, default=str)
        
        # Truncate intelligently if needed
        if len(config_json) > 20000:
            config_json = config_json[:20000] + "\n... (truncated)"
        
        prompt = f"""Analyze this {iac_type.upper()} infrastructure.

ACTUAL RESOURCE CONFIGURATIONS:
{config_json}

Based on these ACTUAL configurations:

1. **Explain each resource** - What does it do? What do its specific settings mean?
   (e.g., if you see an IAM policy with s3:*, explain what that grants)

2. **Map the data flow** - How do resources connect? What permissions enable this?

3. **Find security issues** - Be specific! Reference actual config values.
   (e.g., "security group allows 0.0.0.0/0 on port 22" not just "SSH is open")

4. **Educate** - Explain cloud concepts inline for security practitioners who
   may not know what IAM roles, security groups, or VPCs are.

Respond with valid JSON only."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
        
        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse LLM response: {e}",
                "raw_response": response_text[:500] if 'response_text' in locals() else None,
            }
        except anthropic.APIError as e:
            return {"error": f"LLM API error: {e}"}
    
    def _analyze_diff_with_llm(self, context: dict) -> dict:
        """Analyze a PR diff."""
        
        prompt = f"""Analyze this infrastructure PR diff.

CHANGES DETECTED:
- Added resources: {context['changes'].get('added', [])}
- Removed resources: {context['changes'].get('removed', [])}
- Modified resources: {context['changes'].get('modified', [])}

RAW DIFF:
```
{context['raw_diff']}
```

Focus on:
1. What is this PR trying to accomplish?
2. What new access or exposure does it create?
3. Security concerns with the CHANGES (reference specific lines)
4. Explain affected services inline

Respond with valid JSON."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            
            response_text = response.content[0].text
            
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
        
        except (json.JSONDecodeError, anthropic.APIError) as e:
            return {"error": str(e)}
    
    def _build_result(self, llm_analysis: dict, raw_data: dict) -> ReviewResult:
        """Build ReviewResult from LLM analysis."""
        
        if "error" in llm_analysis:
            return ReviewResult(
                architecture_summary=f"Analysis error: {llm_analysis['error']}",
                service_interactions=[],
                security_findings=[],
                service_explanations={},
                raw_resources=raw_data,
            )
        
        findings = []
        for f in llm_analysis.get("security_findings", []):
            findings.append(SecurityFinding(
                severity=f.get("severity", "info"),
                title=f.get("title", "Unknown"),
                description=f.get("description", ""),
                affected_resources=f.get("affected_resources", []),
                recommendation=f.get("recommendation", ""),
                concept_references=f.get("concepts", []),
            ))
        
        return ReviewResult(
            architecture_summary=llm_analysis.get("architecture_summary", "Unable to generate summary"),
            service_interactions=llm_analysis.get("service_interactions", []),
            security_findings=findings,
            service_explanations=llm_analysis.get("service_explanations", {}),
            raw_resources=raw_data,
        )
    
    def format_review_markdown(self, result: ReviewResult) -> str:
        """Format review result as markdown."""
        
        lines = []
        
        # Architecture Summary
        lines.append("## 🏗️ Architecture Summary\n")
        lines.append(result.architecture_summary)
        lines.append("")
        
        # Service Explanations (dynamic from LLM)
        if result.service_explanations:
            lines.append("## 📖 What Each Resource Does\n")
            for addr, explanation in result.service_explanations.items():
                lines.append(f"### `{addr}`")
                lines.append(explanation)
                lines.append("")
        
        # Service Interactions
        if result.service_interactions:
            lines.append("## 🔄 Data Flow & Permissions\n")
            for interaction in result.service_interactions:
                lines.append(f"**{interaction.get('from', '?')}** → **{interaction.get('to', '?')}**")
                lines.append(f"- {interaction.get('interaction', '')}")
                if interaction.get('permissions'):
                    lines.append(f"- *Permissions:* {interaction['permissions']}")
                lines.append("")
        
        # Security Findings
        if result.security_findings:
            lines.append("## 🔐 Security Findings\n")
            
            for severity in ["critical", "high", "medium", "low", "info"]:
                severity_findings = [f for f in result.security_findings if f.severity == severity]
                if severity_findings:
                    emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "ℹ️"}
                    lines.append(f"### {emoji.get(severity, '')} {severity.upper()}\n")
                    
                    for finding in severity_findings:
                        lines.append(f"**{finding.title}**\n")
                        lines.append(finding.description)
                        lines.append(f"\n*Affected:* `{', '.join(finding.affected_resources)}`")
                        lines.append(f"\n*Fix:* {finding.recommendation}\n")
        
        return "\n".join(lines)
