# Example AWS Infrastructure for SecReviewAgent Demo
# A simple serverless API with Lambda, DynamoDB, and API Gateway

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# DynamoDB Table for storing data
resource "aws_dynamodb_table" "events" {
  name         = "events-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "event_id"

  attribute {
    name = "event_id"
    type = "S"
  }

  tags = {
    Name        = "events-table"
    Environment = "production"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "event-processor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda to access DynamoDB
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "dynamodb-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.events.arn
      }
    ]
  })
}

# Lambda Function
resource "aws_lambda_function" "processor" {
  function_name = "event-processor"
  runtime       = "python3.11"
  handler       = "handler.process"
  role          = aws_iam_role.lambda_role.arn
  
  filename = "processor.zip"

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.events.name
    }
  }

  tags = {
    Name = "event-processor"
  }
}

# API Gateway
resource "aws_apigatewayv2_api" "api" {
  name          = "events-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.processor.invoke_arn
}

resource "aws_apigatewayv2_route" "post" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /events"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "prod"
  auto_deploy = true
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.processor.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}

# S3 Bucket with potential security issue (public access)
resource "aws_s3_bucket" "uploads" {
  bucket = "my-uploads-bucket-example"

  tags = {
    Name = "uploads-bucket"
  }
}

# This is a security concern - public access
resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = false  # Security issue!
  block_public_policy     = false  # Security issue!
  ignore_public_acls      = false
  restrict_public_buckets = false
}
