#!/bin/bash

# Exit on error
set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REMOTE_USER="root"
REMOTE_HOST="185.190.39.223"
REMOTE_PATH="/home/health"
LOCAL_PATH="$(pwd)"

echo -e "${GREEN}=== Health AI Backend Deployment ===${NC}\n"

# Check if SSH key is configured
echo -e "${YELLOW}Checking SSH connection...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${REMOTE_USER}@${REMOTE_HOST} exit 2>/dev/null; then
    echo -e "${YELLOW}Warning: SSH key authentication not configured.${NC}"
    echo -e "${YELLOW}You will be prompted for password multiple times.${NC}"
    echo -e "${YELLOW}Consider setting up SSH key authentication for passwordless deployment.${NC}\n"
fi

# Confirm deployment
echo -e "${YELLOW}This will deploy to: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}${NC}"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
fi

# Create remote directory if it doesn't exist
echo -e "\n${GREEN}Step 1: Creating remote directory...${NC}"
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_PATH}"

# Copy files using rsync
echo -e "\n${GREEN}Step 2: Copying files to remote server...${NC}"
rsync -avz --progress \
    --exclude='.git/' \
    --exclude='.venv/' \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.log' \
    --exclude='.vscode/' \
    --exclude='.idea/' \
    --exclude='*.swp' \
    --exclude='*.swo' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='db.sqlite3' \
    --exclude='.coverage' \
    --exclude='.pytest_cache/' \
    --exclude='staticfiles/' \
    --exclude='media/' \
    ./ \
    ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

echo -e "\n${GREEN}Step 3: Deploying application on remote server...${NC}"

# SSH into remote server and run docker-compose
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
set -e

cd /home/health

echo "Checking for .env file..."
if [ ! -f .env ]; then
    echo "No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit /home/health/.env with production values!"
fi

echo "Stopping existing containers..."
docker-compose down || true

echo "Building and starting containers..."
docker-compose up -d --build

echo "Waiting for services to be healthy..."
sleep 5

echo "Checking container status..."
docker-compose ps

echo "Deployment completed!"
ENDSSH

echo -e "\n${GREEN}=== Deployment Successful ===${NC}"
echo -e "${GREEN}Application is running at: http://${REMOTE_HOST}:8000${NC}"
echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "  View logs:     ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_PATH} && docker-compose logs -f'"
echo -e "  Restart:       ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_PATH} && docker-compose restart'"
echo -e "  Stop:          ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_PATH} && docker-compose down'"
echo -e "  Shell access:  ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_PATH} && docker-compose exec web bash'"
echo -e "\n${YELLOW}⚠️  Don't forget to configure production settings in ${REMOTE_PATH}/.env${NC}"
