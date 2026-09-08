#!/bin/bash

# NexusCore State Engine - Google Cloud Deployment Script
# This script automates deployment to Google Cloud Platform

set -e

echo "🚀 NexusCore State Engine - Google Cloud Deployment"
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Project setup
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
read -p "Enter your desired service name (e.g., nexuscore-chat): " SERVICE_NAME
read -p "Enter your desired region (e.g., us-central1): " REGION

echo -e "${YELLOW}Configuring gcloud...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required Google Cloud APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
echo ""
echo "Next steps:"
echo "1. Update your frontend to use: $SERVICE_URL/api"
echo "2. Access the chat interface at: $SERVICE_URL/chat.html"
echo "3. Access the dashboard at: $SERVICE_URL"
