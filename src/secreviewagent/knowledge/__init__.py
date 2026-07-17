"""AWS and Kubernetes knowledge base for educational explanations."""

from secreviewagent.knowledge.aws_services import AWS_SERVICES, get_service_info
from secreviewagent.knowledge.security_concepts import SECURITY_CONCEPTS, get_concept_explanation

__all__ = [
    "AWS_SERVICES",
    "get_service_info",
    "SECURITY_CONCEPTS", 
    "get_concept_explanation",
]
