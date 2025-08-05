# Functional Documentation

## Overview
The Framework Editor App provides a user-friendly web interface for managing control frameworks and their mappings to authoritative sources. It is designed for compliance, audit, and risk management professionals.

## Main Features

### 1. Upload Framework Data
- Users can upload an Excel file containing:
  - A `ccf` sheet (control framework data)
  - An `as-mapping` sheet (authoritative source mappings)
- The app validates and loads the data into a local database.

### 2. Framework View
- Browse, search, and filter control framework entries by domain or keyword.
- View details for each control, including:
  - Control ID, Name, Description
  - Domain, Mapping to Frameworks, Implementation Guidance
- Edit control details and mappings interactively.

### 3. Authoritative Sources View
- Browse, search, and filter mappings to external frameworks (authoritative sources).
- Filter by framework, reference, and classification.
- View and edit mapping details, including:
  - Framework, Reference, Requirement
  - Mapping text, Classification, Justifications
  - Linked control IDs

### 4. Data Export
- Export the current state of the framework and mappings to an Excel file.
- Download the file for offline use or sharing.

### 5. Navigation & Data Management
- Sidebar navigation for switching between Framework and Authoritative Sources views.
- Data management tools for uploading new data or exporting current data.

## Typical Workflow
1. Launch the app and upload a framework Excel file.
2. Browse and search controls or mappings.
3. Edit details as needed.
4. Export the updated data to Excel.

## Error Handling
- The app provides user-friendly error messages for invalid uploads, missing columns, or other issues.
- All actions are performed interactively with immediate feedback in the UI. 