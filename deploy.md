# Deployment Guide

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- (Optional) Docker
- Port 8501 available (default for Streamlit)

## Local Deployment

1. **Clone the repository**
   ```sh
   git clone <repo-url>
   cd ccf-editor
   ```
2. **Install dependencies**
   ```sh
   pip install -r framework-editor-docker/requirements.txt
   ```
3. **Run the app**
   ```sh
   streamlit run framework-editor-docker/framework-editor-app/app.py
   ```
4. **Access the app**
   - Open your browser and go to [http://localhost:8501](http://localhost:8501)

## Docker Deployment

1. **Build the Docker image**
   ```sh
   docker build -t framework-editor framework-editor-docker/
   ```
2. **Run the Docker container**
   ```sh
   docker run -p 8501:8501 framework-editor
   ```
3. **Access the app**
   - Open your browser and go to [http://localhost:8501](http://localhost:8501)

## Excel File Format
- Prepare an Excel file with two sheets:
  - `ccf` (Control Framework):
    - Control ID, Domain, Control Name, Control Description, Mapping to Frameworks, Implementation Guidance
  - `as-mapping` (Authoritative Sources):
    - framework, reference, requirement, mapping, classification, classification_justification, mapping_justification, control_ids

## Troubleshooting
- **Port already in use:**
  - Change the port with `--server.port` for Streamlit or `-p` for Docker.
- **Permission errors:**
  - Ensure you have read/write access to the data directory.
- **Excel upload errors:**
  - Check that your file has the required sheets and columns.
- **Docker issues:**
  - Check container logs with `docker logs <container-id>`

## Support
- Review error messages in the app UI
- Check logs for more details
- Ensure your Excel file matches the required format 