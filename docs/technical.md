# Technical Documentation

## Architecture Overview

The Framework Editor App is a modular Python application built with Streamlit for the web UI and SQLite for local data storage. It is structured into three main modules:

- `app.py`: Main entry point, orchestrates UI and backend logic
- `backend.py`: Handles all data management, database operations, and business logic
- `frontend.py`: Contains all Streamlit UI components and user interaction logic

## Main Modules

### 1. app.py
- Initializes the database and UI
- Manages Streamlit session state for navigation and selections
- Delegates data operations to `FrameworkDatabase` (backend.py)
- Delegates UI rendering to `FrameworkUI` (frontend.py)
- Handles error reporting in the UI

### 2. backend.py
- Defines the `FrameworkDatabase` class
  - Manages a SQLite database with two main tables:
    - `control_framework`: Stores control framework data
    - `as_mapping`: Stores mappings to authoritative sources
  - Handles data import/export from/to Excel using pandas
  - Provides CRUD operations for controls and mappings
  - Implements filtering, searching, and mapping logic
- Defines the `MappingProcessor` class for parsing mapping text

### 3. frontend.py
- Defines the `FrameworkUI` class
  - Sets up Streamlit page configuration and custom CSS
  - Renders the sidebar for navigation and data management
  - Provides UI for uploading, exporting, and navigating data
  - Renders tables, detail views, and forms for editing controls and mappings
  - Implements search, filter, and selection components

## Data Flow

1. User uploads an Excel file via the UI
2. `FrameworkDatabase.load_data_from_excel()` parses and stores data in SQLite
3. UI components in `FrameworkUI` display and allow editing of data
4. Edits are written back to the database via backend methods
5. User can export the current database state to Excel

## Key Technologies
- **Python 3**
- **Streamlit** (UI)
- **Pandas** (data manipulation)
- **SQLite** (database)
- **Docker** (optional, for deployment)

## Extensibility
- To add new fields: update the database schema in `backend.py`, adjust import/export logic, and update UI in `frontend.py`
- To change the UI: modify or extend methods in `FrameworkUI`
- To add new data sources: extend backend logic in `backend.py` 