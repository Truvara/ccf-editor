import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional, Set

class FrameworkUI:
    @staticmethod
    def set_page_config():
        """Configure the Streamlit page settings"""
        st.set_page_config(
            page_title="Control Framework Editor",
            page_icon="🔒",
            layout="wide"
        )

    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling"""
        st.markdown("""
            <style>
            .main {
                padding-top: 2rem;
            }
            .stDataFrame {
                width: 100%;
            }
            .mapping-editor {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            /* Style for clickable Control IDs */
            table a {
                color: #ff4b4b;
                text-decoration: none;
                font-weight: 500;
            }
            table a:hover {
                text-decoration: underline;
            }
            /* Improve table styling */
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th {
                background-color: #1E1E1E;
                padding: 8px;
                text-align: left;
                color: white;
            }
            td {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            tr:hover {
                background-color: #2A2A2A;
            }
            /* Overlay styles */
            .overlay-container {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0, 0, 0, 0.8);
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 2rem;
            }
            .overlay-content {
                background-color: #1E1E1E;
                border-radius: 10px;
                width: 90%;
                max-width: 1400px;
                height: 90vh;
                overflow-y: auto;
                padding: 2rem;
                position: relative;
            }
            .overlay-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #333;
            }
            .overlay-close {
                color: #ff4b4b;
                font-size: 24px;
                cursor: pointer;
                background: none;
                border: none;
                padding: 0.5rem;
            }
            .overlay-body {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
            }
            .control-details, .mapping-section {
                background-color: #2A2A2A;
                padding: 1.5rem;
                border-radius: 8px;
            }
            .stTextInput input, .stTextArea textarea {
                background-color: #1E1E1E !important;
                border-color: #333 !important;
                color: #E0E0E0 !important;
            }
            .stTabs {
                background-color: #2A2A2A;
                padding: 1rem;
                border-radius: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_sidebar(db) -> None:
        """Display the sidebar with navigation and filters"""
        st.sidebar.markdown("# 🔒 Control Framework Editor")
        
        # Data Management section
        st.sidebar.write("### Data Management")
        
        # File uploader for loading data
        uploaded_file = st.sidebar.file_uploader(
            "Upload Framework Excel",
            type=['xlsx'],
            help="Upload an Excel file with 'ccf' and 'as-mapping' sheets in the required format"
        )
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if uploaded_file is not None:
                if st.button("Load Data", help="Load data from uploaded Excel file"):
                    with st.spinner('Loading framework data...'):
                        success, message = db.load_data_from_excel(uploaded_file)
                        if success:
                            st.success(f"""
                                ✅ Framework loaded successfully!
                                
                                File: {uploaded_file.name}
                                Size: {round(uploaded_file.size/1024, 2)} KB
                                
                                {message}
                            """)
                            st.balloons()  # Add a celebratory effect
                            st.rerun()
                        else:
                            st.error(f"""
                                ❌ Error loading framework:
                                
                                {message}
                                
                                Please ensure your Excel file has:
                                - A 'ccf' sheet with control framework data
                                - An 'as-mapping' sheet with mapping data
                                - All required columns in both sheets
                            """)
            else:
                st.info("👆 Please upload an Excel file to load framework data")
        
        with col2:
            if st.button("Export", help="Export framework data to Excel"):
                with st.spinner('Preparing framework export...'):
                    success, excel_data = db.save_to_excel()
                    if success:
                        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"framework_export_{timestamp}.xlsx"
                        
                        # Create download button for the Excel file
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Click to download the framework data as Excel file"
                        )
                        
                        st.success(f"""
                            ✅ Framework exported successfully!
                            
                            Click the download button above to save the file.
                            Filename: {filename}
                        """)
                    else:
                        st.error(f"""
                            ❌ Error exporting framework:
                            
                            {excel_data}
                            
                            Please try again or contact support if the issue persists.
                        """)
        
        st.sidebar.markdown("---")
        
        # Navigation section with selected state
        st.sidebar.write("### Navigation")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button(
                "Framework", 
                use_container_width=True,
                type="primary" if st.session_state.page == "Framework" else "secondary"
            ):
                st.session_state.page = "Framework"
                st.rerun()
        with col2:
            if st.button(
                "Auth Sources", 
                use_container_width=True,
                type="primary" if st.session_state.page == "Authoritative Sources" else "secondary"
            ):
                st.session_state.page = "Authoritative Sources"
                st.rerun()

    @staticmethod
    def show_framework_controls(df: pd.DataFrame) -> None:
        """Display the framework controls dataframe"""
        if df.empty:
            st.info("No controls found for the selected filters")
            return
        
        display_columns = [
            'Control_ID', 'Domain', 'Control_Name', 'Control_Description',
            'Mapping_to_Frameworks', 'Implementation_Guidance'
        ]
        
        # Ensure all required columns exist
        for col in display_columns:
            if col not in df.columns:
                df[col] = ''
        
        df_display = df[display_columns].copy()
        
        st.dataframe(
            df_display,
            hide_index=True,
            use_container_width=True,
            height=400,
            column_config={
                "Control_ID": st.column_config.Column("Control ID", width="medium"),
                "Domain": st.column_config.Column("Domain", width="medium"),
                "Control_Name": st.column_config.Column("Control Name", width="large"),
                "Control_Description": st.column_config.Column("Control Description", width="large"),
                "Mapping_to_Frameworks": st.column_config.Column("Mapping to Frameworks", width="large"),
                "Implementation_Guidance": st.column_config.Column("Implementation Guidance", width="large")
            }
        )

    @staticmethod
    def show_control_details(control_data: Dict[str, Any], db) -> None:
        """Display detailed view of a control"""
        # Reset form data when control changes
        control_key = control_data['Control_ID']
        if 'current_control' not in st.session_state or st.session_state.current_control != control_key:
            st.session_state.current_control = control_key
            st.session_state.form_data = {
                'control_name': control_data['Control_Name'],
                'control_desc': control_data['Control_Description'],
                'implementation_guidance': control_data['Implementation_Guidance'],
                'mappings_to_add': [],
                'mappings_to_remove': []
            }

        # Create two columns for split view
        col1, col2 = st.columns([1, 1])
        
        # Left column: Control Information
        with col1:
            st.subheader("Control Information")
            with st.container():
                st.text_input("Control ID", control_data['Control_ID'], disabled=True)
                st.text_input("Domain", control_data['Domain'], disabled=True)
                
                # Add unique keys for each control's form fields
                st.text_input(
                    "Control Name",
                    value=st.session_state.form_data['control_name'],
                    key=f"control_name_{control_key}",
                    on_change=lambda: setattr(st.session_state.form_data, 'control_name', 
                        st.session_state[f"control_name_{control_key}"])
                )
                
                st.text_area(
                    "Control Description",
                    value=st.session_state.form_data['control_desc'],
                    key=f"control_desc_{control_key}",
                    height=150,
                    on_change=lambda: setattr(st.session_state.form_data, 'control_desc', 
                        st.session_state[f"control_desc_{control_key}"])
                )
                
                st.text_area(
                    "Implementation Guidance",
                    value=st.session_state.form_data['implementation_guidance'],
                    key=f"implementation_guidance_{control_key}",
                    height=150,
                    on_change=lambda: setattr(st.session_state.form_data, 'implementation_guidance', 
                        st.session_state[f"implementation_guidance_{control_key}"])
                )

        # Right column: Mappings
        with col2:
            st.subheader("Framework Mappings")
            
            # Show current mappings first
            st.markdown("#### Current Mappings")
            mappings = db.get_control_mappings(control_data['Control_ID'])
            
            if mappings:
                # Convert mappings to DataFrame
                df_mappings = pd.DataFrame(mappings)
                
                # Display mappings in a table format
                for idx, row in df_mappings.iterrows():
                    cols = st.columns([3, 3, 8, 2])
                    with cols[0]:
                        st.write(row['framework_source'])
                    with cols[1]:
                        st.write(row['reference'])
                    with cols[2]:
                        with st.expander("View Requirement"):
                            st.write(row['requirement'])
                    with cols[3]:
                        if st.checkbox("Remove", key=f"remove_{control_key}_{row['framework_source']}_{row['reference']}"):
                            mapping_key = (row['framework_source'], row['reference'])
                            if mapping_key not in st.session_state.form_data['mappings_to_remove']:
                                st.session_state.form_data['mappings_to_remove'].append(mapping_key)
            else:
                st.info("No mappings found for this control")

            # Add new mapping section
            st.markdown("---")
            st.markdown("#### Add New Mapping")

            # Framework selection
            framework_source = st.selectbox(
                "Framework",
                db.get_all_framework_sources(),
                key=f"new_mapping_framework_{control_key}"
            )

            if framework_source:
                references = db.get_framework_references(framework_source)
                if references['references']:
                    reference_options = {
                        ref: f"{ref}: {references['descriptions'].get(ref, '')[:100]}..."
                        for ref in references['references']
                    }
                    
                    selected_ref = st.selectbox(
                        "Reference",
                        options=list(reference_options.keys()),
                        format_func=lambda x: reference_options[x],
                        key=f"new_mapping_reference_{control_key}"
                    )
                    
                    if selected_ref:
                        with st.expander("View Full Requirement", expanded=True):
                            st.info(references['descriptions'].get(selected_ref, ''))
                        
                        if st.checkbox("Add", key=f"add_{control_key}_{framework_source}_{selected_ref}"):
                            mapping_data = {
                                'framework': framework_source,
                                'reference': selected_ref,
                                'requirement': references['descriptions'].get(selected_ref, '')
                            }
                            if mapping_data not in st.session_state.form_data['mappings_to_add']:
                                st.session_state.form_data['mappings_to_add'].append(mapping_data)

            # Action button at the bottom
            st.markdown("---")
            
            # Save button with green color
            if st.button("Save Changes", type="primary", use_container_width=True):
                # Save control information
                success, message = db.update_control(control_data['Control_ID'], {
                    'Control_Name': st.session_state.form_data['control_name'],
                    'Control_Description': st.session_state.form_data['control_desc'],
                    'Implementation_Guidance': st.session_state.form_data['implementation_guidance']
                })
                
                # Process mappings to remove
                for framework, reference in st.session_state.form_data['mappings_to_remove']:
                    db.remove_control_mapping(control_data['Control_ID'], framework, reference)
                
                # Process mappings to add
                for mapping in st.session_state.form_data['mappings_to_add']:
                    db.add_control_mapping(
                        control_data['Control_ID'],
                        mapping['framework'],
                        mapping['reference'],
                        mapping['requirement']
                    )
                
                if success:
                    st.success("✅ All changes saved successfully!")
                    # Clear the form data
                    st.session_state.form_data = {
                        'control_name': control_data['Control_Name'],
                        'control_desc': control_data['Control_Description'],
                        'implementation_guidance': control_data['Implementation_Guidance'],
                        'mappings_to_add': [],
                        'mappings_to_remove': []
                    }
                    st.rerun()
                else:
                    st.error(f"❌ Error saving changes: {message}")

    @staticmethod
    def show_mapping_view(df: pd.DataFrame) -> None:
        """Display the mapping view dataframe"""
        if df.empty:
            st.info("No mappings found for the selected filters")
            return

        # Prepare display columns and their configuration
        column_config = {
            "framework": st.column_config.Column("Framework", width="medium"),
            "reference": st.column_config.Column("Reference", width="medium"),
            "requirement": st.column_config.Column("Requirement", width="large"),
            "classification": st.column_config.Column("Classification", width="medium"),
            "classification_justification": st.column_config.Column("Classification Justification", width="large"),
            "mapping_justification": st.column_config.Column("Mapping Justification", width="large"),
            "control_ids": st.column_config.Column("Mapped Controls", width="large")
        }

        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            height=400,
            column_config=column_config
        )

    @staticmethod
    def show_mapping_details(reference_data: Dict[str, Any], db) -> None:
        """Display detailed view of a mapping reference"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Reference Information")
            with st.container():
                st.markdown(f"**Framework**: {reference_data['framework']}")
                st.markdown(f"**Reference ID**: {reference_data['reference']}")
                st.markdown("---")
                
                requirement = st.text_area(
                    "Requirement Text",
                    reference_data['requirement'],
                    height=150
                )
                
                classification = st.selectbox(
                    "Type",
                    ["", "compliance", "business"],
                    index=["", "compliance", "business"].index(reference_data['classification']) if reference_data['classification'] else 0
                )
                
                classification_justification = st.text_area(
                    "Classification Justification",
                    reference_data['classification_justification'],
                    height=100
                )

                mapping_justification = st.text_area(
                    "Mapping Justification",
                    reference_data.get('mapping_justification', ''),
                    height=100
                )
                
                if st.button("Save Reference Information", use_container_width=True, type="primary"):
                    try:
                        db.update_reference(
                            reference_data['framework'],
                            reference_data['reference'],
                            requirement,
                            classification,
                            classification_justification,
                            mapping_justification
                        )
                        st.success("Reference information saved successfully")
                    except Exception as e:
                        st.error(f"Error saving reference information: {str(e)}")

    @staticmethod
    def show_search_bar() -> str:
        """Display the search bar and return the search term"""
        return st.text_input("🔍 Search", "")

    @staticmethod
    def show_domain_filters(domains: List[str], selected_domain: str) -> str:
        """Display domain filters and return the selected domain"""
        st.sidebar.write("### Domain Filters")
        
        # Single selectbox for domain selection
        selected = st.sidebar.selectbox(
            "Select Domain",
            domains,
            index=domains.index(selected_domain) if selected_domain in domains else 0
        )
        
        return selected

    @staticmethod
    def show_framework_filters(sources: List[str], selected_sources: Set[str]) -> Set[str]:
        """Display framework filters and return the selected sources"""
        st.sidebar.write("### Framework Filters")
        
        # Single selectbox for framework selection
        selected_source = st.sidebar.selectbox(
            "Select Framework",
            ["All Frameworks"] + sources,
            index=0
        )
        
        # Return the selected source as a set
        if selected_source == "All Frameworks":
            return set(sources)
        return {selected_source}

    @staticmethod
    def show_classification_filters() -> List[str]:
        """Display classification filters and return selected classifications"""
        st.sidebar.write("### Classification Filters")
        
        # Initialize classification filters in session state if not exists
        if 'selected_classifications' not in st.session_state:
            st.session_state.selected_classifications = []
        
        classifications = ["business", "compliance"]  # Only business and compliance
        selected = []
        
        for classification in classifications:
            if st.sidebar.checkbox(
                classification.capitalize(),
                value=classification in st.session_state.selected_classifications,
                key=f"filter_{classification}"
            ):
                selected.append(classification)
        
        st.session_state.selected_classifications = selected
        return selected

    @staticmethod
    def show_as_details(reference_data: Dict[str, Any], db) -> None:
        """Display detailed view of an authoritative source reference"""
        # Reset form data when reference changes
        reference_key = f"{reference_data['framework']}:{reference_data['reference']}"
        if 'current_reference' not in st.session_state or st.session_state.current_reference != reference_key:
            st.session_state.current_reference = reference_key
            st.session_state.as_form_data = {
                'requirement': reference_data['requirement'],
                'classification': reference_data.get('classification', 'business'),
                'classification_justification': reference_data.get('classification_justification', ''),
                'mapping_justification': reference_data.get('mapping_justification', ''),
                'mappings_to_add': [],
                'mappings_to_remove': []
            }
        
        # Create two columns for split view
        col1, col2 = st.columns([1, 1])
        
        # Left column: Reference Information
        with col1:
            st.subheader("Reference Information")
            with st.container():
                st.text_input("Framework", reference_data['framework'], disabled=True)
                st.text_input("Reference ID", reference_data['reference'], disabled=True)
                st.text_area(
                    "Requirement",
                    value=st.session_state.as_form_data['requirement'],
                    key=f"requirement_{st.session_state.current_reference}",
                    height=150,
                    on_change=lambda: setattr(st.session_state.as_form_data, 'requirement', st.session_state[f"requirement_{st.session_state.current_reference}"])
                )
                
                # Only business and compliance options
                classification_options = ["business", "compliance"]
                current_classification = reference_data.get('classification', 'business')
                
                # Find the index of the current classification
                try:
                    classification_index = classification_options.index(current_classification.lower())
                except ValueError:
                    classification_index = 0  # Default to first option if not found
                
                # Update the classification in form data
                selected_classification = st.selectbox(
                    "Classification",
                    ["business", "compliance"],
                    index=["business", "compliance"].index(st.session_state.as_form_data['classification']),
                    key=f"classification_{st.session_state.current_reference}"
                )
                st.session_state.as_form_data['classification'] = selected_classification
                
                st.text_area(
                    "Classification Justification",
                    value=st.session_state.as_form_data['classification_justification'],
                    key=f"classification_justification_{st.session_state.current_reference}",
                    height=100,
                    on_change=lambda: setattr(st.session_state.as_form_data, 'classification_justification', st.session_state[f"classification_justification_{st.session_state.current_reference}"])
                )
                st.text_area(
                    "Mapping Justification",
                    value=st.session_state.as_form_data['mapping_justification'],
                    key=f"mapping_justification_{st.session_state.current_reference}",
                    height=100,
                    on_change=lambda: setattr(st.session_state.as_form_data, 'mapping_justification', st.session_state[f"mapping_justification_{st.session_state.current_reference}"])
                )
                
                if st.button("Save Reference Information", use_container_width=True, type="primary"):
                    success, message = db.update_as_reference(
                        reference_data['framework'],
                        reference_data['reference'],
                        {
                            'requirement': st.session_state.as_form_data['requirement'],
                            'classification': st.session_state.as_form_data['classification'],
                            'classification_justification': st.session_state.as_form_data['classification_justification'],
                            'mapping_justification': st.session_state.as_form_data['mapping_justification']
                        }
                    )
                    if success:
                        st.success("Reference information saved successfully")
                        st.rerun()
                    else:
                        st.error(f"Error saving reference information: {message}")
        
        # Right column: Control Mappings
        with col2:
            st.subheader("Control Mappings")
            
            # Show current mappings first
            st.markdown("#### Current Mappings")
            control_ids = reference_data.get('control_ids', '').split(';') if reference_data.get('control_ids') else []
            
            if control_ids:
                for control_id in control_ids:
                    if control_id.strip():  # Only process non-empty control IDs
                        control_data = db.get_control_details(control_id.strip())
                        if control_data:
                            cols = st.columns([3, 8, 2])
                            with cols[0]:
                                st.write(control_id)
                            with cols[1]:
                                with st.expander("View Control"):
                                    st.write(f"**{control_data['Control_Name']}**")
                                    st.write(control_data['Control_Description'])
                            with cols[2]:
                                if st.checkbox("Remove", key=f"remove_{control_id}"):
                                    if control_id not in st.session_state.as_form_data['mappings_to_remove']:
                                        st.session_state.as_form_data['mappings_to_remove'].append(control_id)
            else:
                st.info("No control mappings found")
            
            # Add new mapping section
            st.markdown("---")
            st.markdown("#### Add New Mapping")
            
            # Control selection
            controls = db.get_all_controls()
            if controls:
                control_options = {
                    control['Control_ID']: f"{control['Control_ID']}: {control['Control_Name'][:100]}..."
                    for control in controls
                }
                
                selected_control = st.selectbox(
                    "Control",
                    options=list(control_options.keys()),
                    format_func=lambda x: control_options[x],
                    key="new_control_mapping"
                )
                
                if selected_control:
                    control_data = db.get_control_details(selected_control)
                    if control_data is not None:
                        with st.expander("View Control Details", expanded=True):
                            st.write(f"**{control_data['Control_Name']}**")
                            st.write(control_data['Control_Description'])
                        
                        if st.checkbox("Add", key=f"add_{selected_control}"):
                            if selected_control not in st.session_state.as_form_data['mappings_to_add']:
                                st.session_state.as_form_data['mappings_to_add'].append(selected_control)
            
            # Save button at the bottom
            st.markdown("---")
            if st.button("Save Mapping Changes", type="primary", use_container_width=True):
                # Process mappings to remove
                for control_id in st.session_state.as_form_data['mappings_to_remove']:
                    db.remove_as_control_mapping(
                        reference_data['framework'],
                        reference_data['reference'],
                        control_id
                    )
                
                # Process mappings to add
                for control_id in st.session_state.as_form_data['mappings_to_add']:
                    db.add_as_control_mapping(
                        reference_data['framework'],
                        reference_data['reference'],
                        control_id
                    )
                
                st.success("Mapping changes saved successfully")
                st.rerun()
