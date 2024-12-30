#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if Rancher Desktop is running
check_rancher() {
    echo "Checking Rancher Desktop status..."
    if ! pgrep -f "Rancher Desktop" > /dev/null; then
        echo -e "${RED}Error: Rancher Desktop is not running.${NC}"
        echo "Please start Rancher Desktop and ensure:"
        echo "1. Container engine is set to 'dockerd (moby)'"
        echo "2. The application has finished starting up"
        exit 1
    fi
    echo -e "${GREEN}✓ Rancher Desktop is running${NC}"
}

# Function to check if docker command is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: docker command not found${NC}"
        echo "Please ensure Rancher Desktop is properly installed and configured"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker command is available${NC}"
}

# Function to ensure data directory exists
ensure_data_dir() {
    if [ ! -d "data" ]; then
        echo "Creating data directory..."
        mkdir -p data
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to create data directory${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ Data directory is ready${NC}"
}

# Main execution
echo -e "${YELLOW}Starting Framework Editor...${NC}"

# Run checks
check_rancher
check_docker
ensure_data_dir

# Stop and remove existing container if it exists
echo "Cleaning up any existing containers..."
docker stop framework-editor 2>/dev/null
docker rm framework-editor 2>/dev/null

# Build the image
echo "Building Docker image..."
if ! docker build -t framework-editor .; then
    echo -e "${RED}Error: Failed to build Docker image${NC}"
    exit 1
fi

# Run the container
echo "Starting container..."
if ! docker run -d \
    --name framework-editor \
    -p 8501:8501 \
    -v "$(pwd)/data:/app/data" \
    framework-editor; then
    echo -e "${RED}Error: Failed to start container${NC}"
    exit 1
fi

# Wait for container to start
echo "Waiting for application to start..."
sleep 5

# Check if container is running
if ! docker ps | grep -q framework-editor; then
    echo -e "${RED}Error: Container failed to start${NC}"
    echo "Checking container logs:"
    docker logs framework-editor
    exit 1
fi

echo -e "${GREEN}✓ Framework Editor is ready!${NC}"
echo "Opening browser..."

# Try different commands to open browser based on OS
if command -v open &> /dev/null; then
    open http://localhost:8501
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8501
else
    echo "Please open http://localhost:8501 in your browser"
fi

# Show container logs
echo -e "${YELLOW}Container logs:${NC}"
docker logs framework-editor

echo -e "\n${GREEN}Setup complete!${NC}"
echo "Access the application at: http://localhost:8501"
echo "To view logs later, run: docker logs framework-editor"
echo "To stop the application, run: docker stop framework-editor" 