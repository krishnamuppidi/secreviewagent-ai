"""
Security Concepts Knowledge Base.

Educational explanations of cloud security concepts for practitioners
who may not have deep cloud-native security experience.
"""

from dataclasses import dataclass


@dataclass
class SecurityConcept:
    """A security concept with educational explanation."""
    
    name: str
    short_description: str
    detailed_explanation: str
    why_it_matters: str
    common_mistakes: list[str]
    best_practices: list[str]


SECURITY_CONCEPTS: dict[str, SecurityConcept] = {
    "least_privilege": SecurityConcept(
        name="Principle of Least Privilege",
        short_description="Grant only the minimum permissions needed to perform a task",
        detailed_explanation="""
The principle of least privilege means giving users, services, and applications only
the permissions they absolutely need to do their job - nothing more. If a Lambda function
only needs to read from a specific S3 bucket, it shouldn't have permissions to write
to S3 or access any other services.

In AWS, this means carefully crafting IAM policies instead of using broad permissions
like "s3:*" (all S3 actions) or Resource: "*" (all resources).
        """.strip(),
        why_it_matters="""
If a service is compromised, the attacker can only do what that service could do.
With least privilege, a compromised Lambda function that only reads from one DynamoDB
table can't suddenly access your S3 buckets or delete your databases.
        """.strip(),
        common_mistakes=[
            "Using managed policies like AdministratorAccess or PowerUserAccess",
            "Granting 'Action: *' or 'Resource: *' in IAM policies",
            "Copying permissions from another role without reviewing them",
            "Not restricting permissions after initial development",
        ],
        best_practices=[
            "Start with zero permissions and add only what's needed",
            "Use specific resource ARNs instead of wildcards",
            "Regularly audit permissions with IAM Access Analyzer",
            "Use conditions to further restrict when permissions apply",
        ],
    ),
    
    "defense_in_depth": SecurityConcept(
        name="Defense in Depth",
        short_description="Multiple layers of security controls that don't rely on any single measure",
        detailed_explanation="""
Defense in depth is a security strategy that uses multiple layers of protection.
If one layer fails, others are still in place. In AWS, this might mean combining:

- Network security (VPCs, security groups, NACLs)
- Identity security (IAM roles, policies)  
- Application security (input validation, authentication)
- Data security (encryption at rest and in transit)
- Monitoring (CloudTrail, GuardDuty, CloudWatch)

Each layer provides protection even if another layer is bypassed or misconfigured.
        """.strip(),
        why_it_matters="""
No single security control is perfect. Attackers often chain together multiple
small vulnerabilities. Defense in depth ensures that a failure in one control
doesn't lead to complete compromise.
        """.strip(),
        common_mistakes=[
            "Relying solely on network isolation without IAM controls",
            "Assuming encryption means data is secure without access controls",
            "Not monitoring and alerting on security events",
            "Treating security as a one-time setup rather than ongoing",
        ],
        best_practices=[
            "Combine network, identity, and application-level controls",
            "Use encryption AND access controls for sensitive data",
            "Enable logging at all layers",
            "Regularly test that each layer works independently",
        ],
    ),
    
    "public_exposure": SecurityConcept(
        name="Public Exposure / Internet Accessibility",
        short_description="Resources accessible from the public internet without authentication",
        detailed_explanation="""
Public exposure means a resource can be reached from anywhere on the internet.
In AWS, this happens when:

- Security groups allow 0.0.0.0/0 (any IP) on a port
- S3 buckets have public access enabled
- RDS databases are marked as 'publicly accessible'
- Resources are in public subnets with public IPs

Not all public exposure is bad - web servers need to be reachable. But databases,
internal APIs, and admin interfaces should never be publicly accessible.
        """.strip(),
        why_it_matters="""
Publicly exposed resources are constantly scanned by attackers. A misconfigured
security group or public S3 bucket has been the cause of countless data breaches.
Even with authentication, unnecessary public exposure increases attack surface.
        """.strip(),
        common_mistakes=[
            "Making RDS databases publicly accessible 'for testing'",
            "Opening 0.0.0.0/0 on SSH (port 22) for convenience",
            "Not enabling S3 Block Public Access at the account level",
            "Putting application servers in public subnets",
        ],
        best_practices=[
            "Use private subnets for databases and backend services",
            "Access private resources via bastion hosts or VPN",
            "Enable S3 Block Public Access at the account level",
            "Use AWS Systems Manager Session Manager instead of SSH",
        ],
    ),
    
    "encryption": SecurityConcept(
        name="Encryption (At Rest & In Transit)",
        short_description="Protecting data by converting it to an unreadable format",
        detailed_explanation="""
Encryption protects data in two scenarios:

**At Rest:** Data stored on disk (S3 objects, EBS volumes, RDS databases).
AWS provides server-side encryption (SSE) that automatically encrypts data
when stored and decrypts when accessed by authorized users.

**In Transit:** Data moving across networks. HTTPS/TLS encrypts traffic between
clients and servers, preventing eavesdropping. AWS services communicate over
TLS by default, but you must enforce it for your own applications.

Encryption without proper key management is ineffective. AWS KMS (Key Management Service)
lets you control who can use encryption keys.
        """.strip(),
        why_it_matters="""
Encryption protects against:
- Data theft if physical hardware is stolen
- Network eavesdropping
- Unauthorized access by cloud provider employees
- Compliance requirements (HIPAA, PCI-DSS, GDPR)
        """.strip(),
        common_mistakes=[
            "Assuming data is encrypted without verifying",
            "Using the default AWS-managed key instead of customer-managed keys",
            "Not enforcing TLS for internal service communication",
            "Storing encryption keys alongside encrypted data",
        ],
        best_practices=[
            "Enable encryption at rest for all data stores",
            "Enforce TLS 1.2+ for all network communication",
            "Use customer-managed KMS keys for sensitive data",
            "Audit key usage with CloudTrail",
        ],
    ),
    
    "irsa": SecurityConcept(
        name="IRSA (IAM Roles for Service Accounts)",
        short_description="Kubernetes pods assume IAM roles without long-term credentials",
        detailed_explanation="""
IRSA (IAM Roles for Service Accounts) is an EKS feature that lets Kubernetes pods
assume IAM roles. Instead of sharing node-level IAM permissions or storing AWS
credentials in secrets, each pod can have its own IAM role.

How it works:
1. Create an IAM role with a trust policy for your EKS OIDC provider
2. Annotate a Kubernetes ServiceAccount with the role ARN
3. Pods using that ServiceAccount automatically get temporary credentials

This is the AWS equivalent of workload identity in other cloud providers.
        """.strip(),
        why_it_matters="""
Without IRSA, all pods on a node share the same IAM permissions (from the node's
instance profile). This violates least privilege - a compromised pod could access
resources intended for other pods. IRSA enables per-pod permissions.
        """.strip(),
        common_mistakes=[
            "Attaching IAM policies to EC2 node roles instead of using IRSA",
            "Storing AWS credentials in Kubernetes secrets",
            "Using overly permissive IAM roles with IRSA",
            "Not restricting which ServiceAccounts can assume which roles",
        ],
        best_practices=[
            "Use IRSA for all AWS API access from EKS pods",
            "Create dedicated IAM roles for each workload",
            "Use conditions in IAM trust policies to restrict access",
            "Audit IRSA role usage with CloudTrail",
        ],
    ),
    
    "network_segmentation": SecurityConcept(
        name="Network Segmentation",
        short_description="Dividing a network into isolated segments to limit lateral movement",
        detailed_explanation="""
Network segmentation divides your infrastructure into isolated segments, each with
its own access controls. In AWS:

- **VPCs** isolate entire environments (prod vs dev)
- **Subnets** separate tiers (public web, private app, private data)
- **Security Groups** control traffic between resources
- **NACLs** provide subnet-level filtering
- **Network Policies** (Kubernetes) control pod-to-pod traffic

The goal is to ensure that compromising one component doesn't give access to everything.
        """.strip(),
        why_it_matters="""
Attackers who breach one system often move laterally to find more valuable targets.
Network segmentation limits this movement. If your web server is compromised,
proper segmentation prevents the attacker from directly accessing your database.
        """.strip(),
        common_mistakes=[
            "Putting all resources in the same security group",
            "Not using private subnets for backend services",
            "Allowing all traffic between security groups",
            "Not implementing Kubernetes network policies",
        ],
        best_practices=[
            "Use separate VPCs for production and non-production",
            "Put databases in private subnets with no internet access",
            "Use security groups as identity (reference groups, not IPs)",
            "Implement default-deny network policies in Kubernetes",
        ],
    ),
}


def get_concept_explanation(concept_key: str) -> SecurityConcept | None:
    """
    Get explanation of a security concept.
    
    Args:
        concept_key: Concept identifier (e.g., 'least_privilege', 'encryption')
    
    Returns:
        SecurityConcept if found, None otherwise
    """
    return SECURITY_CONCEPTS.get(concept_key.lower())
