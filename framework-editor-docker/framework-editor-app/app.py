import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import streamlit as st
from backend import FrameworkDatabase
from frontend import FrameworkUI

def search_controls(df, search_term):
    """Filter controls based on search term"""
    if not search_term:
        return df
    
    search_term = search_term.lower()
    return df[
        df['Control_ID'].str.lower().str.contains(search_term) |
        df['Control_Name'].str.lower().str.contains(search_term) |
        df['Control_Description'].str.lower().str.contains(search_term)
    ]

def main():
    # Initialize database
    db = FrameworkDatabase()
    db.init_db()
    
    # Initialize UI
    FrameworkUI.set_page_config()
    FrameworkUI.apply_custom_css()
    
    # Initialize session state for page if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "Framework"
    
    # Show sidebar
    FrameworkUI.show_sidebar(db)
    
    # Add this at the start of main(), after initializing session state for page
    if 'control_selector_index' not in st.session_state:
        st.session_state.control_selector_index = 0
    
    try:
        if st.session_state.page == "Framework":
            # Get unique domains for filtering
            domains = db.get_domains()
            
            # Search bar
            search_term = FrameworkUI.show_search_bar()
            
            # Domain selector in sidebar
            selected_domain = FrameworkUI.show_domain_filters(domains, "All Domains")
            
            # Framework view with domain filter
            df = db.get_controls(selected_domain if selected_domain != "All Domains" else None)
            
            if not df.empty:
                # Filter based on search
                filtered_df = search_controls(df, search_term)
                
                # Show framework controls
                FrameworkUI.show_framework_controls(filtered_df)
                
                # Create control selection options
                control_options = [""] + [
                    f"{row['Control_ID']}: {row['Control_Name']}" 
                    for _, row in filtered_df.iterrows()
                ]
                
                # Add a dropdown to select control
                selected_control = st.selectbox(
                    "Select a control to view details",
                    control_options,
                    index=st.session_state.control_selector_index,
                    key="control_selector"
                )
                
                # Show details if control is selected
                if selected_control:
                    if ":" in selected_control:
                        control_id = selected_control.split(":")[0].strip()
                        st.session_state.selected_control = control_id
                        control_data = db.get_control_details(control_id)
                        if control_data is not None:
                            FrameworkUI.show_control_details(control_data, db)
                    else:
                        keys_to_remove = [
                            'form_data', 
                            'selected_control', 
                            'new_mapping_framework',
                            'new_mapping_reference'
                        ]
                        for key in list(st.session_state.keys()):
                            if (key in keys_to_remove or 
                                key.startswith('remove_') or 
                                key.startswith('add_') or 
                                key.startswith('filter_')):
                                del st.session_state[key]
        
        else:  # Authoritative Sources view
            # Get unique sources for filtering
            sources = db.get_frameworks()
            
            # Search bar for authoritative sources
            search_term = FrameworkUI.show_search_bar()
            
            # Framework selector in sidebar
            selected_sources = FrameworkUI.show_framework_filters(sources, set())
            
            # Classification filters
            selected_classifications = FrameworkUI.show_classification_filters()
            
            # Get mapping data based on selected sources
            df = db.get_mapping_data(list(selected_sources))
            
            if not df.empty:
                # Filter based on search
                if search_term:
                    filtered_df = search_controls(df, search_term)
                else:
                    filtered_df = df
                
                # Apply classification filters if any are selected
                if selected_classifications:
                    filtered_df = filtered_df[filtered_df['classification'].isin(selected_classifications)]
                
                # Show mapping view
                FrameworkUI.show_mapping_view(filtered_df)
                
                # Add reference selector
                reference_options = [""] + [
                    f"{row['framework']}: {row['reference']}" 
                    for _, row in filtered_df.iterrows()
                ]
                
                # Add a key that includes the selected classifications to force refresh
                selector_key = f"reference_selector_{'-'.join(selected_classifications)}"
                selected_reference = st.selectbox(
                    "Select a reference to view details",
                    reference_options,
                    index=0,
                    key=selector_key
                )
                
                # Show details if reference is selected
                if selected_reference and ":" in selected_reference:
                    framework, reference = selected_reference.split(":", 1)
                    framework = framework.strip()
                    reference = reference.strip()
                    
                    # Clear the form data when switching references
                    reference_key = f"{framework}:{reference}"
                    if 'current_reference' not in st.session_state or st.session_state.current_reference != reference_key:
                        if 'as_form_data' in st.session_state:
                            del st.session_state.as_form_data
                    
                    reference_data = db.get_reference_details(framework, reference)
                    if reference_data is not None:
                        FrameworkUI.show_as_details(reference_data, db)
                
                # Add a close button for the details view if reference is selected
                if "selected_reference" in st.session_state:
                    col1, col2 = st.columns([6, 1])
                    with col2:
                        if st.button("Close Details", key="close_details", use_container_width=True):
                            del st.session_state.selected_reference
                            st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 