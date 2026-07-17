"""
Terraform HCL Parser for SecReviewAgent.

Parses Terraform configurations to extract:
- Resources and their types
- IAM policies and permissions
- Security groups and network rules
- Resource relationships and references
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import hcl2


@dataclass
class TerraformResource:
    """Represents a Terraform resource."""
    
    resource_type: str
    name: str
    address: str
    attributes: dict = field(default_factory=dict)
    references: list = field(default_factory=list)
    
    @property
    def aws_service(self) -> str | None:
        """Extract AWS service name from resource type."""
        if self.resource_type.startswith("aws_"):
            parts = self.resource_type[4:].split("_")
            return parts[0] if parts else None
        return None
    
    @property
    def is_compute(self) -> bool:
        """Check if resource is a compute resource."""
        compute_types = {
            "aws_lambda_function", "aws_ecs_service", "aws_ecs_task_definition",
            "aws_instance", "aws_eks_cluster", "aws_batch_job_definition",
        }
        return self.resource_type in compute_types
    
    @property
    def is_data_store(self) -> bool:
        """Check if resource is a data store."""
        data_types = {
            "aws_db_instance", "aws_rds_cluster", "aws_dynamodb_table",
            "aws_s3_bucket", "aws_elasticache_cluster", "aws_redshift_cluster",
            "aws_secretsmanager_secret", "aws_ssm_parameter",
        }
        return self.resource_type in data_types
    
    @property
    def is_iam(self) -> bool:
        """Check if resource is IAM-related."""
        return self.resource_type.startswith("aws_iam_")
    
    @property
    def is_network(self) -> bool:
        """Check if resource is network-related."""
        network_types = {
            "aws_security_group", "aws_security_group_rule", "aws_vpc",
            "aws_subnet", "aws_route_table", "aws_network_acl",
            "aws_vpc_endpoint", "aws_nat_gateway", "aws_internet_gateway",
        }
        return self.resource_type in network_types


@dataclass
class IAMPolicy:
    """Parsed IAM policy with statements."""
    
    name: str
    statements: list = field(default_factory=list)
    
    def get_allowed_actions(self) -> list[str]:
        """Get all allowed actions."""
        actions = []
        for stmt in self.statements:
            if stmt.get("Effect") == "Allow":
                stmt_actions = stmt.get("Action", [])
                if isinstance(stmt_actions, str):
                    actions.append(stmt_actions)
                else:
                    actions.extend(stmt_actions)
        return actions
    
    def get_allowed_resources(self) -> list[str]:
        """Get all allowed resources."""
        resources = []
        for stmt in self.statements:
            if stmt.get("Effect") == "Allow":
                stmt_resources = stmt.get("Resource", [])
                if isinstance(stmt_resources, str):
                    resources.append(stmt_resources)
                else:
                    resources.extend(stmt_resources)
        return resources


@dataclass
class SecurityGroupRule:
    """Security group rule."""
    
    direction: str  # ingress or egress
    protocol: str
    from_port: int
    to_port: int
    cidr_blocks: list = field(default_factory=list)
    source_security_group_id: str | None = None
    description: str | None = None
    
    @property
    def is_public(self) -> bool:
        """Check if rule allows public access."""
        return "0.0.0.0/0" in self.cidr_blocks or "::/0" in self.cidr_blocks


class TerraformParser:
    """
    Parse Terraform configurations and extract security-relevant information.
    
    This parser is designed to understand Terraform HCL and extract:
    - All resources and their relationships
    - IAM policies and permissions granted
    - Security groups and network access rules
    - Data stores and who can access them
    """
    
    def __init__(self):
        self.resources: dict[str, TerraformResource] = {}
        self.iam_policies: dict[str, IAMPolicy] = {}
        self.security_groups: dict[str, list[SecurityGroupRule]] = {}
        self.variables: dict[str, Any] = {}
        self.locals: dict[str, Any] = {}
    
    def parse_directory(self, directory: str) -> dict[str, TerraformResource]:
        """Parse all Terraform files in a directory."""
        tf_dir = Path(directory)
        
        if not tf_dir.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        # Parse .tf files
        for tf_file in tf_dir.glob("**/*.tf"):
            self._parse_file(tf_file)
        
        # Parse .tf.json files
        for tf_json in tf_dir.glob("**/*.tf.json"):
            self._parse_json_file(tf_json)
        
        # Resolve references
        self._resolve_references()
        
        return self.resources
    
    def parse_diff(self, diff_content: str) -> dict:
        """
        Parse a git diff of Terraform files.
        
        Returns dict with 'added', 'removed', 'modified' resources.
        """
        added = []
        removed = []
        modified = []
        
        current_file = None
        in_hunk = False
        added_lines = []
        removed_lines = []
        
        for line in diff_content.split("\n"):
            if line.startswith("diff --git"):
                # New file
                if current_file and (added_lines or removed_lines):
                    changes = self._analyze_diff_lines(added_lines, removed_lines)
                    added.extend(changes.get("added", []))
                    removed.extend(changes.get("removed", []))
                    modified.extend(changes.get("modified", []))
                
                match = re.search(r"b/(.+\.tf)$", line)
                current_file = match.group(1) if match else None
                added_lines = []
                removed_lines = []
            
            elif line.startswith("@@"):
                in_hunk = True
            
            elif in_hunk and current_file:
                if line.startswith("+") and not line.startswith("+++"):
                    added_lines.append(line[1:])
                elif line.startswith("-") and not line.startswith("---"):
                    removed_lines.append(line[1:])
        
        # Process last file
        if current_file and (added_lines or removed_lines):
            changes = self._analyze_diff_lines(added_lines, removed_lines)
            added.extend(changes.get("added", []))
            removed.extend(changes.get("removed", []))
            modified.extend(changes.get("modified", []))
        
        return {"added": added, "removed": removed, "modified": modified}
    
    def _parse_file(self, filepath: Path) -> None:
        """Parse a single .tf file."""
        try:
            with open(filepath) as f:
                parsed = hcl2.load(f)
                self._process_parsed_hcl(parsed)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
    
    def _parse_json_file(self, filepath: Path) -> None:
        """Parse a .tf.json file."""
        try:
            with open(filepath) as f:
                parsed = json.load(f)
                self._process_parsed_hcl(parsed)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
    
    def _process_parsed_hcl(self, parsed: dict) -> None:
        """Process parsed HCL content."""
        # Extract variables
        for var_block in parsed.get("variable", []):
            for var_name, var_config in var_block.items():
                default = var_config.get("default") if isinstance(var_config, dict) else None
                self.variables[var_name] = default
        
        # Extract locals
        for local_block in parsed.get("locals", []):
            if isinstance(local_block, dict):
                self.locals.update(local_block)
        
        # Extract resources
        for resource_block in parsed.get("resource", []):
            for resource_type, resources in resource_block.items():
                for resource_name, config in resources.items():
                    address = f"{resource_type}.{resource_name}"
                    references = self._extract_references(config)
                    
                    resource = TerraformResource(
                        resource_type=resource_type,
                        name=resource_name,
                        address=address,
                        attributes=config if isinstance(config, dict) else {},
                        references=references,
                    )
                    
                    self.resources[address] = resource
                    
                    # Special handling for IAM policies
                    if resource_type in ("aws_iam_policy", "aws_iam_role_policy"):
                        self._extract_iam_policy(resource)
                    
                    # Special handling for security groups
                    if resource_type == "aws_security_group":
                        self._extract_security_group_rules(resource)
    
    def _extract_references(self, config: Any, refs: list | None = None) -> list[str]:
        """Recursively extract resource references from config."""
        if refs is None:
            refs = []
        
        if isinstance(config, str):
            patterns = [
                r'\$\{([a-z_]+\.[a-z0-9_-]+)(?:\.[a-z_]+)?\}',
                r'([a-z_]+\.[a-z0-9_-]+)(?:\.[a-z_]+)?',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, config, re.IGNORECASE)
                for match in matches:
                    if "." in match and not match.startswith(("var.", "local.", "data.")):
                        refs.append(match)
        
        elif isinstance(config, dict):
            for value in config.values():
                self._extract_references(value, refs)
        
        elif isinstance(config, list):
            for item in config:
                self._extract_references(item, refs)
        
        return list(set(refs))
    
    def _extract_iam_policy(self, resource: TerraformResource) -> None:
        """Extract and parse IAM policy statements."""
        policy_doc = resource.attributes.get("policy")
        
        if isinstance(policy_doc, dict):
            statements = policy_doc.get("Statement", [])
            self.iam_policies[resource.address] = IAMPolicy(
                name=resource.name,
                statements=statements,
            )
        elif isinstance(policy_doc, str):
            policy_str = policy_doc.strip()
            
            # Handle ${jsonencode({...})} wrapper
            if policy_str.startswith("${jsonencode(") and policy_str.endswith(")}"):
                policy_str = policy_str[len("${jsonencode("):-len(")}")]
            
            try:
                policy = json.loads(policy_str)
                statements = policy.get("Statement", [])
                self.iam_policies[resource.address] = IAMPolicy(
                    name=resource.name,
                    statements=statements,
                )
            except json.JSONDecodeError:
                pass
    
    def _extract_security_group_rules(self, resource: TerraformResource) -> None:
        """Extract security group rules."""
        rules = []
        
        for ingress in resource.attributes.get("ingress", []):
            if isinstance(ingress, dict):
                rules.append(SecurityGroupRule(
                    direction="ingress",
                    protocol=ingress.get("protocol", "tcp"),
                    from_port=ingress.get("from_port", 0),
                    to_port=ingress.get("to_port", 0),
                    cidr_blocks=ingress.get("cidr_blocks", []),
                    source_security_group_id=ingress.get("security_groups", [None])[0]
                        if ingress.get("security_groups") else None,
                    description=ingress.get("description"),
                ))
        
        for egress in resource.attributes.get("egress", []):
            if isinstance(egress, dict):
                rules.append(SecurityGroupRule(
                    direction="egress",
                    protocol=egress.get("protocol", "tcp"),
                    from_port=egress.get("from_port", 0),
                    to_port=egress.get("to_port", 0),
                    cidr_blocks=egress.get("cidr_blocks", []),
                    source_security_group_id=egress.get("security_groups", [None])[0]
                        if egress.get("security_groups") else None,
                    description=egress.get("description"),
                ))
        
        self.security_groups[resource.address] = rules
    
    def _resolve_references(self) -> None:
        """Resolve and validate resource references."""
        for resource in self.resources.values():
            resolved_refs = []
            for ref in resource.references:
                if ref in self.resources:
                    resolved_refs.append(ref)
                else:
                    for addr in self.resources:
                        if addr.startswith(ref) or ref.startswith(addr.split(".")[0]):
                            resolved_refs.append(addr)
                            break
            resource.references = resolved_refs
    
    def _analyze_diff_lines(self, added: list[str], removed: list[str]) -> dict:
        """Analyze diff lines to identify resource changes."""
        result = {"added": [], "removed": [], "modified": []}
        
        added_text = "\n".join(added)
        removed_text = "\n".join(removed)
        
        # Find resource blocks in added lines
        added_resources = re.findall(
            r'resource\s+"(\w+)"\s+"(\w+)"',
            added_text
        )
        for rtype, rname in added_resources:
            result["added"].append(f"{rtype}.{rname}")
        
        # Find resource blocks in removed lines
        removed_resources = re.findall(
            r'resource\s+"(\w+)"\s+"(\w+)"',
            removed_text
        )
        for rtype, rname in removed_resources:
            if f"{rtype}.{rname}" in result["added"]:
                result["added"].remove(f"{rtype}.{rname}")
                result["modified"].append(f"{rtype}.{rname}")
            else:
                result["removed"].append(f"{rtype}.{rname}")
        
        return result
    
    def get_compute_resources(self) -> list[TerraformResource]:
        """Get all compute resources."""
        return [r for r in self.resources.values() if r.is_compute]
    
    def get_data_stores(self) -> list[TerraformResource]:
        """Get all data store resources."""
        return [r for r in self.resources.values() if r.is_data_store]
    
    def get_iam_resources(self) -> list[TerraformResource]:
        """Get all IAM resources."""
        return [r for r in self.resources.values() if r.is_iam]
    
    def get_network_resources(self) -> list[TerraformResource]:
        """Get all network resources."""
        return [r for r in self.resources.values() if r.is_network]
    
    def to_dict(self) -> dict:
        """Export parsed data as dictionary."""
        return {
            "resources": {
                addr: {
                    "type": r.resource_type,
                    "name": r.name,
                    "aws_service": r.aws_service,
                    "references": r.references,
                    "is_compute": r.is_compute,
                    "is_data_store": r.is_data_store,
                    "is_iam": r.is_iam,
                    "is_network": r.is_network,
                }
                for addr, r in self.resources.items()
            },
            "iam_policies": {
                addr: {
                    "name": p.name,
                    "allowed_actions": p.get_allowed_actions(),
                    "allowed_resources": p.get_allowed_resources(),
                }
                for addr, p in self.iam_policies.items()
            },
            "security_groups": {
                addr: [
                    {
                        "direction": r.direction,
                        "protocol": r.protocol,
                        "from_port": r.from_port,
                        "to_port": r.to_port,
                        "cidr_blocks": r.cidr_blocks,
                        "is_public": r.is_public,
                    }
                    for r in rules
                ]
                for addr, rules in self.security_groups.items()
            },
        }
