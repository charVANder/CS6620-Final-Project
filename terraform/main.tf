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
  access_key = "test"
  secret_key = "test"
  s3_use_path_style = true
  skip_credentials_validation = true
  skip_metadata_api_check = true
  skip_requesting_account_id = true

  endpoints {
    apigateway = "http://localhost:4566"
    lambda = "http://localhost:4566"
    s3 = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    iam = "http://localhost:4566"
  }
}

# DynamoDB cache table
resource "aws_dynamodb_table" "cache_table" {
  name = "drug-interactions-cache"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "interaction_key"

  attribute {
    name = "interaction_key"
    type = "S"
  }

  tags = {
    Name = "DrugInteractionCache"
  }
}

# Lambda function
resource "aws_lambda_function" "drug_checker" {
  filename = "app.zip"
  function_name = "drug-interaction-checker"
  role = aws_iam_role.lambda_role.arn
  handler = "app.lambda_handler"
  runtime = "python3.9"
  timeout = 30

  environment {
    variables = {
      MOCK_API_URL = "http://host.docker.internal:5001"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy]
}

resource "aws_lambda_function_url" "drug_checker_url" {
  function_name = aws_lambda_function.drug_checker.function_name
  authorization_type = "NONE"
}

output "function_url" {
  value = aws_lambda_function_url.drug_checker_url.function_url
}

# IAM role
resource "aws_iam_role" "lambda_role" {
  name = "drug_checker_lambda_role"

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

# IAM policy
resource "aws_iam_policy" "lambda_policy" {
  name = "drug_checker_lambda_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream", 
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = aws_dynamodb_table.cache_table.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# API Gateway
resource "aws_api_gateway_rest_api" "drug_checker_api" {
  name = "drug-interaction-checker"
}

resource "aws_api_gateway_method" "root_method" {
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  resource_id = aws_api_gateway_rest_api.drug_checker_api.root_resource_id
  http_method = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  parent_id = aws_api_gateway_rest_api.drug_checker_api.root_resource_id
  path_part = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "proxy_integration" {
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_method.http_method

  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.drug_checker.invoke_arn
}

resource "aws_api_gateway_integration" "root_integration" {
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  resource_id = aws_api_gateway_rest_api.drug_checker_api.root_resource_id
  http_method = aws_api_gateway_method.root_method.http_method

  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.drug_checker.invoke_arn
}

resource "aws_api_gateway_deployment" "drug_checker_deploy" {
  depends_on = [
    aws_api_gateway_integration.root_integration,
    aws_api_gateway_integration.proxy_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.drug_checker_api.id
  stage_name  = "dev"
}

resource "aws_lambda_permission" "api_gw_root" {
  statement_id  = "AllowExecutionFromAPIGatewayRoot"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.drug_checker.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.drug_checker_api.execution_arn}/*/ANY"
}

resource "aws_lambda_permission" "api_gw_proxy" {
  statement_id  = "AllowExecutionFromAPIGatewayProxy"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.drug_checker.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.drug_checker_api.execution_arn}/*/ANY/*"
}

# Output the API Gateway URL
output "api_gateway_url" {
  value = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.drug_checker_api.id}/dev/_user_request_/"
}