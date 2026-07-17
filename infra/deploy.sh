#!/bin/bash
# Deploy SecReviewAgent to AWS

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying SecReviewAgent${NC}"

# Check for tfvars
if [ ! -f terraform.tfvars ]; then
    echo -e "${YELLOW}⚠️  No terraform.tfvars found${NC}"
    echo "Copy terraform.tfvars.example to terraform.tfvars and fill in values"
    exit 1
fi

# Build Lambda layer
echo -e "\n${GREEN}📦 Building Lambda layer...${NC}"
bash build-layer.sh

# Terraform init
echo -e "\n${GREEN}🔧 Terraform init...${NC}"
terraform init

# Terraform plan
echo -e "\n${GREEN}📋 Terraform plan...${NC}"
terraform plan -out=tfplan

# Confirm
read -p "Apply changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted"
    exit 1
fi

# Terraform apply
echo -e "\n${GREEN}🚀 Terraform apply...${NC}"
terraform apply tfplan

# Output webhook URL
echo -e "\n${GREEN}✅ Deployment complete!${NC}"
echo ""
terraform output

echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Copy the webhook_url above"
echo "2. Go to your GitHub repo → Settings → Webhooks → Add webhook"
echo "3. Payload URL: <webhook_url>"
echo "4. Content type: application/json"
echo "5. Secret: (same as github_webhook_secret in tfvars)"
echo "6. Events: Select 'Pull requests'"
