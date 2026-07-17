"""
SecReviewAgent - Educational IaC Security Review Agent for Pull Requests

An LLM-powered agent that reviews Infrastructure-as-Code changes and explains
them to security practitioners who may not be cloud experts.

KEY DESIGN: No static knowledge base. The LLM reads actual Terraform/K8s configs
and explains what each resource does based on its real configuration values.
"""

__version__ = "0.2.0"  # Bump for dynamic knowledge approach
__author__ = "Naga Krishna Reddy Muppidi"
__email__ = ""

from secreviewagent.agents.review_agent import SecReviewAgent
from secreviewagent.parsers.terraform import TerraformParser
from secreviewagent.parsers.kubernetes import KubernetesParser

__all__ = [
    "SecReviewAgent",
    "TerraformParser",
    "KubernetesParser",
]
