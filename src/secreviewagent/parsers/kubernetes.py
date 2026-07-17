"""
Kubernetes YAML Parser for SecReviewAgent.

Parses Kubernetes manifests to extract:
- Deployments, Services, Pods
- RBAC (Roles, RoleBindings, ServiceAccounts)
- NetworkPolicies
- IRSA annotations (EKS)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class K8sResource:
    """Represents a Kubernetes resource."""
    
    api_version: str
    kind: str
    name: str
    namespace: str = "default"
    labels: dict = field(default_factory=dict)
    annotations: dict = field(default_factory=dict)
    spec: dict = field(default_factory=dict)
    
    @property
    def address(self) -> str:
        """Get unique address for this resource."""
        return f"k8s:{self.namespace}/{self.kind.lower()}/{self.name}"
    
    @property
    def irsa_role_arn(self) -> str | None:
        """Get IRSA role ARN if present (EKS)."""
        return self.annotations.get("eks.amazonaws.com/role-arn")
    
    @property
    def is_workload(self) -> bool:
        """Check if resource is a workload."""
        return self.kind in ("Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Pod")
    
    @property
    def is_rbac(self) -> bool:
        """Check if resource is RBAC-related."""
        return self.kind in ("Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding", "ServiceAccount")
    
    @property
    def is_network(self) -> bool:
        """Check if resource is network-related."""
        return self.kind in ("NetworkPolicy", "Ingress", "Service")


@dataclass
class RBACBinding:
    """RBAC binding between subject and role."""
    
    subject_kind: str  # ServiceAccount, User, Group
    subject_name: str
    subject_namespace: str | None
    role_kind: str  # Role, ClusterRole
    role_name: str
    binding_name: str
    binding_namespace: str | None


@dataclass
class NetworkPolicyRule:
    """Network policy rule."""
    
    policy_name: str
    direction: str  # ingress or egress
    pod_selector: dict
    peer_selector: dict | None = None
    namespace_selector: dict | None = None
    ip_block: dict | None = None
    ports: list = field(default_factory=list)


class KubernetesParser:
    """
    Parse Kubernetes manifests and extract security-relevant information.
    
    Extracts:
    - Workloads and their service accounts
    - RBAC bindings (who can do what)
    - Network policies (what can talk to what)
    - IRSA annotations (AWS IAM roles for service accounts)
    """
    
    def __init__(self):
        self.resources: dict[str, K8sResource] = {}
        self.rbac_bindings: list[RBACBinding] = []
        self.network_policies: list[NetworkPolicyRule] = []
        self.service_account_roles: dict[str, str] = {}  # SA -> IAM role ARN
    
    def parse_directory(self, directory: str) -> dict[str, K8sResource]:
        """Parse all YAML files in a directory."""
        k8s_dir = Path(directory)
        
        if not k8s_dir.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        for yaml_file in k8s_dir.glob("**/*.yaml"):
            self._parse_file(yaml_file)
        
        for yml_file in k8s_dir.glob("**/*.yml"):
            self._parse_file(yml_file)
        
        return self.resources
    
    def parse_manifest(self, content: str) -> dict[str, K8sResource]:
        """Parse a YAML manifest string."""
        try:
            docs = list(yaml.safe_load_all(content))
            for doc in docs:
                if doc and isinstance(doc, dict):
                    self._process_resource(doc)
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML: {e}")
        
        return self.resources
    
    def _parse_file(self, filepath: Path) -> None:
        """Parse a single YAML file."""
        try:
            with open(filepath) as f:
                docs = list(yaml.safe_load_all(f))
                for doc in docs:
                    if doc and isinstance(doc, dict):
                        self._process_resource(doc)
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
    
    def _process_resource(self, doc: dict) -> None:
        """Process a single Kubernetes resource document."""
        api_version = doc.get("apiVersion", "")
        kind = doc.get("kind", "")
        metadata = doc.get("metadata", {})
        spec = doc.get("spec", {})
        
        if not kind:
            return
        
        name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        labels = metadata.get("labels", {})
        annotations = metadata.get("annotations", {})
        
        resource = K8sResource(
            api_version=api_version,
            kind=kind,
            name=name,
            namespace=namespace,
            labels=labels,
            annotations=annotations,
            spec=spec,
        )
        
        self.resources[resource.address] = resource
        
        # Extract IRSA annotations from ServiceAccounts
        if kind == "ServiceAccount" and resource.irsa_role_arn:
            sa_key = f"{namespace}/{name}"
            self.service_account_roles[sa_key] = resource.irsa_role_arn
        
        # Extract RBAC bindings
        if kind in ("RoleBinding", "ClusterRoleBinding"):
            self._extract_rbac_binding(resource, spec, metadata)
        
        # Extract NetworkPolicy rules
        if kind == "NetworkPolicy":
            self._extract_network_policy(resource, spec)
    
    def _extract_rbac_binding(self, resource: K8sResource, spec: dict, metadata: dict) -> None:
        """Extract RBAC binding information."""
        role_ref = spec.get("roleRef", {})
        subjects = spec.get("subjects", [])
        
        role_kind = role_ref.get("kind", "")
        role_name = role_ref.get("name", "")
        
        for subject in subjects:
            binding = RBACBinding(
                subject_kind=subject.get("kind", ""),
                subject_name=subject.get("name", ""),
                subject_namespace=subject.get("namespace"),
                role_kind=role_kind,
                role_name=role_name,
                binding_name=metadata.get("name", ""),
                binding_namespace=metadata.get("namespace"),
            )
            self.rbac_bindings.append(binding)
    
    def _extract_network_policy(self, resource: K8sResource, spec: dict) -> None:
        """Extract NetworkPolicy rules."""
        pod_selector = spec.get("podSelector", {})
        
        # Ingress rules
        for ingress in spec.get("ingress", []):
            for from_rule in ingress.get("from", [{}]):
                rule = NetworkPolicyRule(
                    policy_name=resource.name,
                    direction="ingress",
                    pod_selector=pod_selector,
                    peer_selector=from_rule.get("podSelector"),
                    namespace_selector=from_rule.get("namespaceSelector"),
                    ip_block=from_rule.get("ipBlock"),
                    ports=ingress.get("ports", []),
                )
                self.network_policies.append(rule)
        
        # Egress rules
        for egress in spec.get("egress", []):
            for to_rule in egress.get("to", [{}]):
                rule = NetworkPolicyRule(
                    policy_name=resource.name,
                    direction="egress",
                    pod_selector=pod_selector,
                    peer_selector=to_rule.get("podSelector"),
                    namespace_selector=to_rule.get("namespaceSelector"),
                    ip_block=to_rule.get("ipBlock"),
                    ports=egress.get("ports", []),
                )
                self.network_policies.append(rule)
    
    def get_workloads(self) -> list[K8sResource]:
        """Get all workload resources."""
        return [r for r in self.resources.values() if r.is_workload]
    
    def get_service_account_for_workload(self, workload: K8sResource) -> str | None:
        """Get the service account used by a workload."""
        spec = workload.spec
        
        # Check pod template spec for Deployments, etc.
        pod_spec = spec.get("template", {}).get("spec", {})
        if not pod_spec:
            pod_spec = spec  # For Pod resources
        
        return pod_spec.get("serviceAccountName", "default")
    
    def get_iam_role_for_workload(self, workload: K8sResource) -> str | None:
        """Get the IAM role ARN for a workload via IRSA."""
        sa_name = self.get_service_account_for_workload(workload)
        if sa_name:
            sa_key = f"{workload.namespace}/{sa_name}"
            return self.service_account_roles.get(sa_key)
        return None
    
    def to_dict(self) -> dict:
        """Export parsed data as dictionary."""
        return {
            "resources": {
                addr: {
                    "kind": r.kind,
                    "name": r.name,
                    "namespace": r.namespace,
                    "is_workload": r.is_workload,
                    "is_rbac": r.is_rbac,
                    "is_network": r.is_network,
                    "irsa_role_arn": r.irsa_role_arn,
                }
                for addr, r in self.resources.items()
            },
            "rbac_bindings": [
                {
                    "subject": f"{b.subject_kind}/{b.subject_namespace or 'cluster'}/{b.subject_name}",
                    "role": f"{b.role_kind}/{b.role_name}",
                    "binding": b.binding_name,
                }
                for b in self.rbac_bindings
            ],
            "service_account_roles": self.service_account_roles,
            "network_policies": [
                {
                    "policy": r.policy_name,
                    "direction": r.direction,
                    "pod_selector": r.pod_selector,
                }
                for r in self.network_policies
            ],
        }
