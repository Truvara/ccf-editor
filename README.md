# Framework Editor App

A Streamlit-based application for editing and managing control frameworks with database persistence.

![image](https://github.com/user-attachments/assets/499f40c6-b077-49ed-a589-7a83fcf1c6c7)

![image](https://github.com/user-attachments/assets/879956a1-d9e2-4916-8d0e-2e6632a4b143)



## Features

- Upload and manage control frameworks via Excel files
- Edit control details and mappings
- Manage authoritative sources
- Export framework data to Excel
- Persistent database storage
- Docker containerized for easy deployment

## Prerequisites

- Rancher Desktop installed on your Mac
  - [Download Rancher Desktop](https://rancherdesktop.io/)
  - Make sure containerization engine is set to "dockerd (moby)"
- 500MB free disk space
- Port 8501 available (or any other port if 8501 is in use)

## Quick Start Guide

### Option 1: Using the Start Script (Recommended)

1. Download and extract this repository to your computer

2. Open Terminal and navigate to the extracted folder:
```bash
cd path/to/framework-editor-docker
```

3. Make the start script executable:
```bash
chmod +x start-app.sh
```

4. Run the start script:
```bash
./start-app.sh
```

The script will:
- Check if Rancher Desktop is running
- Create necessary directories
- Build and start the container
- Open the application in your browser
- Show helpful status messages and logs

### Option 2: Manual Docker Commands

If you prefer to run commands manually:

1. Create data directory:
```bash
mkdir -p data
```

2. Build the Docker image:
```bash
docker build -t framework-editor .
```

3. Run the container:
```bash
docker run -d \
--name framework-editor \
-p 8501:8501 \
-v "$(pwd)/data:/app/data" \
framework-editor
```

4. Access the application:
- Open your browser
- Go to `http://localhost:8501`

## Using the Application

1. Prepare your Excel file with two sheets:
   - `ccf` sheet for Control Framework data
   - `as-mapping` sheet for Authoritative Sources

2. Upload your Excel file through the application interface

3. Edit and manage your framework data

4. Export updated data back to Excel when needed

## Container Management

To stop the container:
```bash
docker stop framework-editor
```

To start it again:
```bash
docker start framework-editor
```

To remove it completely:
```bash
docker stop framework-editor
docker rm framework-editor
```

To view container logs:
```bash
docker logs framework-editor
```

## Excel File Format

To upload framework data, prepare an Excel file with two sheets:

1. `ccf` sheet (Control Framework):
   - Control ID
   - Domain
   - Control Name
   - Control Description
   - Mapping to Frameworks
   - Implementation Guidance

2. `as-mapping` sheet (Authoritative Sources):
   - framework
   - reference
   - requirement
   - mapping
   - classification
   - classification_justification
   - mapping_justification
   - control_ids

## Troubleshooting

1. If port 8501 is already in use:
```bash
docker run -d --name framework-editor -p 8502:8501 -v "$(pwd)/data:/app/data" framework-editor
```
Then access the app at `http://localhost:8502`

2. If you can't access the application:
   - Check if Rancher Desktop is running
   - Verify dockerd is selected as the container engine in Rancher Desktop
   - Check if the container is running: `docker ps`
   - View container logs: `docker logs framework-editor`

3. If data is not persisting:
   - Check if the data directory exists: `ls -la data`
   - Verify the volume mount: `docker inspect framework-editor`
   - Check folder permissions: `ls -la | grep data`

4. If you get permission errors:
   - Check ownership of the data directory: `ls -la data`
   - Fix permissions if needed: `chmod 777 data`

## Support

For issues:
1. Check Rancher Desktop status and logs
2. Verify your Excel file matches the required format
3. Check container logs: `docker logs framework-editor`
4. Ensure data directory permissions are correct

