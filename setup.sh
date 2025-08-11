#!/bin/bash

echo "~~~~~~~~~~Drug Interaction Checker~~~~~~~~~~"

# Clean LocalStack
echo "~~~~~~~~~~Restarting LocalStack~~~~~~~~~~"
docker-compose down
docker-compose up -d
sleep 15

# Flask app for Lambda
echo "~~~~~~~~~~Packaging Flask app~~~~~~~~~~"
mkdir -p temp_build
cp -r app/* temp_build/

# Install dependencies into a temporary build
echo "~~~~~~~~~~Installing Lambda dependencies~~~~~~~~~~"
pip install --target temp_build flask serverless-wsgi boto3 requests

# Lambda package
echo "~~~~~~~~~~Creating Lambda package~~~~~~~~~~"
cd temp_build
zip -r ../terraform/app.zip . -x "*.pyc" "__pycache__/*"
cd ..
rm -rf temp_build

# Deploy infrastructure
echo "Deploying..."
cd terraform
terraform init
terraform apply -auto-approve

echo "~~~~~~~~~~Deployment complete~~~~~~~~~~"