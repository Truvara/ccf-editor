# Framework Editor App

A web-based tool for managing, editing, and mapping control frameworks to authoritative sources. Built with Python and Streamlit, it enables compliance and risk professionals to upload, edit, and export control frameworks and their mappings using Excel files.

## Features
- Upload Excel files with control frameworks and mappings
- Interactive UI for searching, filtering, and editing controls
- Map controls to authoritative sources and vice versa
- Export updated data to Excel
- Easy deployment (local or Docker)

## Quickstart

1. **Install dependencies:**
   - `pip install -r requirements.txt`
2. **Run the app:**
   - `streamlit run framework-editor-docker/framework-editor-app/app.py`
3. **Or use Docker:**
   - `docker build -t framework-editor .`
   - `docker run -p 8501:8501 framework-editor`
4. **Open your browser:**
   - Go to `http://localhost:8501`

