"""Tests for Terraform parser."""

import pytest
from pathlib import Path

from secreviewagent.parsers.terraform import TerraformParser


@pytest.fixture
def example_tf_dir():
    """Path to example Terraform directory."""
    return Path(__file__).parent.parent / "examples" / "terraform"


class TestTerraformParser:
    """Test Terraform parsing functionality."""
    
    def test_parse_directory(self, example_tf_dir):
        """Test parsing a Terraform directory."""
        parser = TerraformParser()
        resources = parser.parse_directory(str(example_tf_dir))
        
        assert len(resources) > 0
    
    def test_finds_lambda_functions(self, example_tf_dir):
        """Test that Lambda functions are found."""
        parser = TerraformParser()
        parser.parse_directory(str(example_tf_dir))
        
        lambdas = parser.get_compute_resources()
        assert any(r.resource_type == "aws_lambda_function" for r in lambdas)
    
    def test_finds_dynamodb_tables(self, example_tf_dir):
        """Test that DynamoDB tables are found."""
        parser = TerraformParser()
        parser.parse_directory(str(example_tf_dir))
        
        data_stores = parser.get_data_stores()
        assert any(r.resource_type == "aws_dynamodb_table" for r in data_stores)
    
    def test_extracts_iam_policies(self, example_tf_dir):
        """Test that IAM policies are extracted."""
        parser = TerraformParser()
        parser.parse_directory(str(example_tf_dir))
        
        assert len(parser.iam_policies) > 0
    
    def test_to_dict(self, example_tf_dir):
        """Test export to dictionary."""
        parser = TerraformParser()
        parser.parse_directory(str(example_tf_dir))
        
        data = parser.to_dict()
        
        assert "resources" in data
        assert "iam_policies" in data
        assert "security_groups" in data
