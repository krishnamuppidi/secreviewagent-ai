"""
AWS Services Knowledge Base.

Educational descriptions of AWS services for security practitioners
who may not be familiar with cloud-native architectures.
"""

from dataclasses import dataclass


@dataclass
class AWSServiceInfo:
    """Information about an AWS service."""
    
    name: str
    short_description: str
    detailed_description: str
    security_considerations: list[str]
    common_use_cases: list[str]
    related_services: list[str]
    terraform_resource_prefix: str


# Knowledge base of AWS services with educational descriptions
AWS_SERVICES: dict[str, AWSServiceInfo] = {
    "lambda": AWSServiceInfo(
        name="AWS Lambda",
        short_description="Serverless compute service that runs code without managing servers",
        detailed_description="""
AWS Lambda is a serverless compute service that lets you run code without provisioning 
or managing servers. You upload your code, and Lambda takes care of everything required 
to run and scale it. Lambda functions are triggered by events (HTTP requests, file uploads, 
database changes, etc.) and only run when needed.

Think of Lambda like hiring a contractor for a specific task instead of a full-time employee.
You only pay for the compute time you consume - there's no charge when your code isn't running.
        """.strip(),
        security_considerations=[
            "Lambda functions run with IAM roles - review what permissions the role grants",
            "Environment variables may contain secrets - check if they're encrypted",
            "VPC configuration affects what the function can access on the network",
            "Function URLs can expose Lambda directly to the internet without API Gateway",
            "Execution timeout and memory limits affect potential abuse scenarios",
        ],
        common_use_cases=[
            "API backends (with API Gateway)",
            "Data processing and ETL",
            "Scheduled tasks (with EventBridge)",
            "Real-time file processing (S3 triggers)",
        ],
        related_services=["api_gateway", "s3", "dynamodb", "sqs", "eventbridge"],
        terraform_resource_prefix="aws_lambda",
    ),
    
    "dynamodb": AWSServiceInfo(
        name="Amazon DynamoDB",
        short_description="Fully managed NoSQL database with single-digit millisecond performance",
        detailed_description="""
DynamoDB is a fully managed NoSQL database that delivers fast and predictable performance.
Unlike traditional SQL databases, DynamoDB stores data as key-value pairs or documents,
making it ideal for applications that need consistent, single-digit millisecond response times.

Think of DynamoDB like a giant, fast dictionary/hash map in the cloud. You look things up
by a key (like a user ID), and you get back the associated data almost instantly.
It automatically scales to handle traffic spikes without any manual intervention.
        """.strip(),
        security_considerations=[
            "IAM policies control who can read/write to tables",
            "Encryption at rest should be enabled (check SSE configuration)",
            "Point-in-time recovery allows restoring data - important for compliance",
            "VPC endpoints can keep traffic private (avoid traversing the internet)",
            "Fine-grained access control can restrict access to specific items",
        ],
        common_use_cases=[
            "User session storage",
            "Shopping carts and user preferences",
            "Gaming leaderboards",
            "IoT data storage",
        ],
        related_services=["lambda", "api_gateway", "kinesis"],
        terraform_resource_prefix="aws_dynamodb",
    ),
    
    "s3": AWSServiceInfo(
        name="Amazon S3",
        short_description="Object storage service for storing and retrieving any amount of data",
        detailed_description="""
S3 (Simple Storage Service) is object storage in the cloud. Unlike a traditional file system
with folders and drives, S3 stores files as "objects" in "buckets". Each object can be up to
5TB and is accessed via a unique URL.

Think of S3 like an infinite hard drive in the cloud. You can store anything - documents,
images, videos, backups, logs - and access them from anywhere. S3 automatically replicates
your data across multiple data centers for durability.
        """.strip(),
        security_considerations=[
            "Bucket policies and ACLs control public access - misconfiguration is a top breach cause",
            "Block Public Access settings should be enabled unless intentionally public",
            "Encryption at rest (SSE-S3, SSE-KMS) protects data on disk",
            "Versioning helps recover from accidental deletions or overwrites",
            "Access logging tracks who accessed what objects",
            "Object Lock prevents deletion (for compliance requirements)",
        ],
        common_use_cases=[
            "Static website hosting",
            "Data lake storage",
            "Backup and disaster recovery",
            "Application assets (images, files)",
        ],
        related_services=["cloudfront", "lambda", "athena", "glacier"],
        terraform_resource_prefix="aws_s3",
    ),
    
    "iam": AWSServiceInfo(
        name="AWS IAM",
        short_description="Identity and access management - controls who can do what in AWS",
        detailed_description="""
IAM (Identity and Access Management) is how you control access to AWS resources. It lets you
create users, groups, and roles, and define what each can do through policies.

Think of IAM like a security badge system. Users are people, roles are like "hats" that 
services can wear to get permissions, and policies are the rules that say "this badge can 
open these doors". IAM roles are especially important because they let AWS services
(like Lambda or EC2) access other AWS resources securely without storing credentials.
        """.strip(),
        security_considerations=[
            "Follow least privilege - grant only the permissions needed",
            "Avoid wildcard (*) permissions in policies",
            "Use roles instead of long-term access keys when possible",
            "Regularly audit unused permissions with IAM Access Analyzer",
            "Enable MFA for human users, especially administrators",
            "Service control policies (SCPs) can set organization-wide guardrails",
        ],
        common_use_cases=[
            "Granting Lambda access to DynamoDB",
            "Allowing EC2 instances to read from S3",
            "Cross-account access",
            "Federation with corporate identity providers",
        ],
        related_services=["organizations", "sso", "secrets_manager"],
        terraform_resource_prefix="aws_iam",
    ),
    
    "security_group": AWSServiceInfo(
        name="Security Groups",
        short_description="Virtual firewalls that control inbound and outbound traffic",
        detailed_description="""
Security groups act as virtual firewalls for your AWS resources. They control what network
traffic can reach your instances, databases, and other resources. Security groups are 
stateful - if you allow inbound traffic, the response is automatically allowed out.

Think of security groups like bouncers at a club. You define rules like "allow anyone from
the internet on port 443" (HTTPS) or "only allow traffic from this other security group".
By default, security groups block all inbound traffic and allow all outbound traffic.
        """.strip(),
        security_considerations=[
            "0.0.0.0/0 means 'open to the entire internet' - use with caution",
            "Limit open ports to only what's necessary",
            "Reference other security groups instead of IP ranges when possible",
            "Use separate security groups for different tiers (web, app, database)",
            "Document the purpose of each rule with descriptions",
        ],
        common_use_cases=[
            "Allowing HTTPS traffic to web servers",
            "Restricting database access to application servers only",
            "Enabling SSH access from specific IP ranges",
        ],
        related_services=["vpc", "ec2", "rds", "ecs"],
        terraform_resource_prefix="aws_security_group",
    ),
    
    "rds": AWSServiceInfo(
        name="Amazon RDS",
        short_description="Managed relational database service (MySQL, PostgreSQL, etc.)",
        detailed_description="""
RDS (Relational Database Service) is a managed database service that makes it easy to set up,
operate, and scale relational databases in the cloud. It handles routine database tasks like
provisioning, patching, backup, recovery, and scaling.

Think of RDS like having a professional database administrator on call 24/7. You choose
your database engine (PostgreSQL, MySQL, SQL Server, etc.), and AWS handles the 
infrastructure. Your applications connect to RDS just like they would to any database.
        """.strip(),
        security_considerations=[
            "Should not be publicly accessible (check publicly_accessible setting)",
            "Use security groups to restrict which resources can connect",
            "Enable encryption at rest and in transit",
            "Enable automated backups and set appropriate retention",
            "Use IAM database authentication when possible",
            "Enable deletion protection for production databases",
        ],
        common_use_cases=[
            "Application databases",
            "Data warehousing (with Aurora)",
            "Legacy application migration",
        ],
        related_services=["ec2", "lambda", "secrets_manager"],
        terraform_resource_prefix="aws_db",
    ),
    
    "secrets_manager": AWSServiceInfo(
        name="AWS Secrets Manager",
        short_description="Securely store and manage secrets like API keys and database passwords",
        detailed_description="""
Secrets Manager helps you protect access to your applications by storing and managing
secrets like database credentials, API keys, and other sensitive data. It can automatically
rotate secrets on a schedule, reducing the risk of credential compromise.

Think of Secrets Manager like a secure vault for your passwords. Instead of hardcoding
credentials in your code or configuration files, your applications retrieve secrets
from Secrets Manager at runtime. If a secret is compromised, you can rotate it without
redeploying your applications.
        """.strip(),
        security_considerations=[
            "IAM policies control who can read secrets",
            "Enable automatic rotation for database credentials",
            "Use resource policies to restrict cross-account access",
            "Monitor secret access with CloudTrail",
            "Don't put secrets in environment variables if Secrets Manager is available",
        ],
        common_use_cases=[
            "Database credentials",
            "API keys for third-party services",
            "SSH keys and certificates",
        ],
        related_services=["rds", "lambda", "ecs", "kms"],
        terraform_resource_prefix="aws_secretsmanager",
    ),
    
    "api_gateway": AWSServiceInfo(
        name="Amazon API Gateway",
        short_description="Create, publish, and manage APIs at any scale",
        detailed_description="""
API Gateway is a fully managed service that makes it easy to create, publish, and manage
APIs. It acts as a "front door" for applications to access backend services like Lambda
functions, EC2 instances, or any HTTP endpoint.

Think of API Gateway like a receptionist for your backend services. It handles
authentication, rate limiting, request validation, and routing. Clients talk to
API Gateway, which forwards requests to the appropriate backend service.
        """.strip(),
        security_considerations=[
            "Enable authentication (IAM, Cognito, or API keys)",
            "Use WAF to protect against common web exploits",
            "Enable request validation to reject malformed requests",
            "Set up throttling to prevent abuse",
            "Use private endpoints for internal APIs",
            "Enable access logging for audit trails",
        ],
        common_use_cases=[
            "REST APIs for web/mobile applications",
            "Microservices communication",
            "WebSocket APIs for real-time apps",
        ],
        related_services=["lambda", "cognito", "waf"],
        terraform_resource_prefix="aws_api_gateway",
    ),
    
    "eks": AWSServiceInfo(
        name="Amazon EKS",
        short_description="Managed Kubernetes service for running containerized applications",
        detailed_description="""
EKS (Elastic Kubernetes Service) is a managed Kubernetes service that makes it easy to run
Kubernetes on AWS without needing to install and operate your own Kubernetes control plane.
Kubernetes is an open-source system for automating deployment, scaling, and management of
containerized applications.

Think of EKS like a shipping container terminal. Kubernetes organizes your application
containers (like shipping containers), decides where to run them, handles failures, and
scales up when needed. EKS manages the complex Kubernetes infrastructure so you can
focus on your applications.
        """.strip(),
        security_considerations=[
            "Use IRSA (IAM Roles for Service Accounts) instead of node-level IAM roles",
            "Enable control plane logging to CloudWatch",
            "Use private endpoint access to keep API server private",
            "Implement network policies to control pod-to-pod traffic",
            "Regularly update Kubernetes version for security patches",
            "Use Pod Security Standards to restrict container privileges",
        ],
        common_use_cases=[
            "Microservices architectures",
            "CI/CD pipelines",
            "Machine learning workloads",
            "Batch processing",
        ],
        related_services=["ecr", "fargate", "alb"],
        terraform_resource_prefix="aws_eks",
    ),
    
    "vpc": AWSServiceInfo(
        name="Amazon VPC",
        short_description="Isolated virtual network where you launch AWS resources",
        detailed_description="""
VPC (Virtual Private Cloud) is your own isolated section of the AWS cloud where you
can launch resources in a virtual network that you define. You have complete control
over your virtual networking environment, including IP address ranges, subnets,
route tables, and network gateways.

Think of a VPC like building your own private data center in the cloud. You decide
the network layout - which subnets are public (accessible from internet) and which
are private (isolated). Resources in the same VPC can communicate with each other
by default, while access from outside is controlled by security groups and NACLs.
        """.strip(),
        security_considerations=[
            "Use private subnets for databases and backend services",
            "Public subnets should only contain load balancers and NAT gateways",
            "VPC Flow Logs help monitor and troubleshoot connectivity",
            "Use VPC endpoints to keep traffic to AWS services private",
            "Network ACLs provide an additional layer of subnet-level filtering",
        ],
        common_use_cases=[
            "Isolating production from development environments",
            "Multi-tier application architectures",
            "Hybrid cloud connectivity (VPN, Direct Connect)",
        ],
        related_services=["subnet", "security_group", "nat_gateway", "transit_gateway"],
        terraform_resource_prefix="aws_vpc",
    ),
}


def get_service_info(service_key: str) -> AWSServiceInfo | None:
    """
    Get information about an AWS service.
    
    Args:
        service_key: Service identifier (e.g., 'lambda', 's3', 'dynamodb')
    
    Returns:
        AWSServiceInfo if found, None otherwise
    """
    return AWS_SERVICES.get(service_key.lower())


def get_service_from_terraform_type(resource_type: str) -> AWSServiceInfo | None:
    """
    Get service info from a Terraform resource type.
    
    Args:
        resource_type: Terraform resource type (e.g., 'aws_lambda_function')
    
    Returns:
        AWSServiceInfo if matched, None otherwise
    """
    if not resource_type.startswith("aws_"):
        return None
    
    # Extract service name from resource type
    parts = resource_type[4:].split("_")
    service_key = parts[0]
    
    # Handle special cases
    service_map = {
        "db": "rds",
        "secretsmanager": "secrets_manager",
        "apigateway": "api_gateway",
        "apigatewayv2": "api_gateway",
    }
    
    service_key = service_map.get(service_key, service_key)
    return get_service_info(service_key)
