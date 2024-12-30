import sqlite3
import pandas as pd
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

class FrameworkDatabase:
    def __init__(self, db_path=None):
        # Use data directory for database
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Set database path
        self.db_path = db_path or os.path.join(data_dir, 'frameworks.db')
        
    def get_connection(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        c = conn.cursor()
        
        # Create control framework table with updated columns
        c.execute('''
            CREATE TABLE IF NOT EXISTS control_framework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Control_ID TEXT NOT NULL,
                Domain TEXT,
                Control_Name TEXT,
                Control_Description TEXT,
                Mapping_to_Frameworks TEXT,
                Implementation_Guidance TEXT,
                UNIQUE(Control_ID)
            )
        ''')
        
        # Create authoritative sources mapping table with all required columns
        c.execute('''
            CREATE TABLE IF NOT EXISTS as_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                framework TEXT NOT NULL,
                reference TEXT NOT NULL,
                requirement TEXT,
                mapping TEXT,
                classification TEXT,
                classification_justification TEXT,
                mapping_justification TEXT,
                control_ids TEXT,
                UNIQUE(framework, reference)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name=?;
        """, (table_name,))
        result = cursor.fetchone() is not None
        conn.close()
        return result
    
    def table_has_data(self, table_name):
        """Check if a table has any data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result
    
    def load_data_from_excel(self, uploaded_file):
        """Load data from uploaded Excel file into database"""
        try:
            # Read Excel file from uploaded file object
            df_framework = pd.read_excel(uploaded_file, sheet_name='ccf')
            df_mapping = pd.read_excel(uploaded_file, sheet_name='as-mapping')
            
            # Get initial counts
            control_count = len(df_framework)
            mapping_count = len(df_mapping)
            
            # Column mappings for the framework
            framework_columns = {
                'Control ID': 'Control_ID',
                'Domain': 'Domain',
                'Control Name': 'Control_Name', 
                'Control Description': 'Control_Description',
                'Mapping to Frameworks': 'Mapping_to_Frameworks',
                'Implementation Guidance': 'Implementation_Guidance'
            }
            
            # Validate required columns
            required_columns = set(framework_columns.keys())
            if not required_columns.issubset(df_framework.columns):
                missing_cols = required_columns - set(df_framework.columns)
                return False, f"Missing required columns in framework sheet: {', '.join(missing_cols)}"
            
            # Rename columns
            df_framework_renamed = df_framework.rename(columns=framework_columns)
            
            # Add missing columns with empty values
            for col in framework_columns.values():
                if col not in df_framework_renamed.columns:
                    df_framework_renamed[col] = ''
            
            # Save framework data to database
            conn = self.get_connection()
            df_framework_renamed.to_sql('control_framework', conn, if_exists='replace', index=False)
            
            # Process authoritative source mappings
            if not df_mapping.empty:
                # Validate required mapping columns
                required_mapping_cols = {'framework', 'reference', 'requirement', 'mapping', 
                                       'classification', 'classification_justification', 
                                       'mapping_justification', 'control_ids'}
                if not required_mapping_cols.issubset(df_mapping.columns):
                    missing_cols = required_mapping_cols - set(df_mapping.columns)
                    return False, f"Missing required columns in mapping sheet: {', '.join(missing_cols)}"
                
                # Ensure all required columns exist
                for col in required_mapping_cols:
                    if col not in df_mapping.columns:
                        df_mapping[col] = ''
                
                # Save mapping data
                df_mapping.to_sql('as_mapping', conn, if_exists='replace', index=False)
            
            conn.close()
            return True, f"""Framework loaded successfully:
            • {control_count} controls loaded
            • {mapping_count} mappings loaded
            • All required columns validated
            • Database updated"""
        except Exception as e:
            return False, f"Error loading data: {str(e)}"
    
    def _process_and_save_as_mappings(self, df_mapping):
        """Process authoritative source mappings and save to as_mapping table"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Clear existing mappings
            cursor.execute('DELETE FROM as_mapping')
            
            # Process each row from the as-mapping sheet
            for _, row in df_mapping.iterrows():
                # Extract control IDs from mapping text using regex
                mapping_text = str(row.get('mapping', '')) if pd.notna(row.get('mapping')) else ''
                
                # Extract control IDs if mapping text exists
                control_ids = None
                if mapping_text:
                    # Use regex to find all control IDs (format: XXX-NN.N)
                    import re
                    control_id_matches = re.findall(r'([A-Z]+-\d+\.\d+)', mapping_text)
                    if control_id_matches:
                        control_ids = ';'.join(control_id_matches)
                
                # Convert any potential NaN values to empty strings
                framework = str(row.get('framework', '')) if pd.notna(row.get('framework')) else ''
                reference = str(row.get('reference', '')) if pd.notna(row.get('reference')) else ''
                requirement = str(row.get('requirement', '')) if pd.notna(row.get('requirement')) else ''
                classification = str(row.get('classification', '')) if pd.notna(row.get('classification')) else ''
                classification_justification = str(row.get('classification_justification', '')) if pd.notna(row.get('classification_justification')) else ''
                mapping_justification = str(row.get('mapping_justification', '')) if pd.notna(row.get('mapping_justification')) else ''
                
                # Insert into as_mapping table
                cursor.execute('''
                    INSERT OR REPLACE INTO as_mapping 
                    (framework, reference, requirement, mapping, classification,
                     classification_justification, mapping_justification, control_ids)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    framework,
                    reference,
                    requirement,
                    mapping_text,
                    classification,
                    classification_justification,
                    mapping_justification,
                    control_ids
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error processing authoritative source mappings: {str(e)}")
            raise e
    
    def save_to_excel(self):
        """Export database data to Excel and return bytes for download"""
        try:
            import io
            
            # Create BytesIO object to store Excel file
            output = io.BytesIO()
            
            conn = self.get_connection()
            
            # Get control framework data
            df_framework = pd.read_sql('SELECT * FROM control_framework', conn)
            df_mapping = pd.read_sql('SELECT * FROM as_mapping', conn)
            
            # Get counts for success message
            control_count = len(df_framework)
            mapping_count = len(df_mapping)
            
            # Drop the id columns
            if 'id' in df_framework.columns:
                df_framework = df_framework.drop('id', axis=1)
            if 'id' in df_mapping.columns:
                df_mapping = df_mapping.drop('id', axis=1)
            
            # Rename columns back to original format for framework sheet
            df_framework_renamed = df_framework.rename(columns={
                'Control_ID': 'Control ID',
                'Domain': 'Domain',
                'Control_Name': 'Control Name',
                'Control_Description': 'Control Description',
                'Mapping_to_Frameworks': 'Mapping to Frameworks',
                'Implementation_Guidance': 'Implementation Guidance'
            })
            
            # Sort framework data by Control ID
            df_framework_renamed = df_framework_renamed.sort_values('Control ID')
            
            # Sort mapping data by framework and reference
            df_mapping = df_mapping.sort_values(['framework', 'reference'])
            
            # Create Excel writer with xlsxwriter engine
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Write framework sheet
                df_framework_renamed.to_excel(writer, sheet_name='ccf', index=False)
                
                # Write mapping sheet
                df_mapping.to_excel(writer, sheet_name='as-mapping', index=False)
                
                # Get workbook and worksheet objects for formatting
                workbook = writer.book
                
                # Format for headers
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D9D9D9',
                    'border': 1
                })
                
                # Format both sheets
                for sheet_name in ['ccf', 'as-mapping']:
                    worksheet = writer.sheets[sheet_name]
                    df = df_framework_renamed if sheet_name == 'ccf' else df_mapping
                    
                    # Apply header format and column widths
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        col_width = max(
                            len(str(value)) * 1.2,
                            df[value].astype(str).str.len().max() * 1.2
                        )
                        worksheet.set_column(col_num, col_num, min(col_width, 50))
                    
                    # Add text wrapping format for data cells
                    wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})
                    worksheet.set_row(0, 30)  # Set header row height
                    for row in range(1, worksheet.dim_rowmax + 1):
                        worksheet.set_row(row, None, wrap_format)
            
            # Get the value of the BytesIO buffer
            excel_data = output.getvalue()
            conn.close()
            
            # Return success with the excel data
            return True, excel_data
        except Exception as e:
            return False, f"""Error exporting framework:
            
            {str(e)}
            
            Please check:
            • Database connection is working
            • You have write permissions
            • Sufficient disk space available"""
    
    def get_controls(self, domain_filter=None):
        """Get controls with optional domain filter"""
        try:
            conn = self.get_connection()
            query = 'SELECT * FROM control_framework'
            params = ()
            
            if domain_filter and domain_filter != "All Domains":
                query += ' WHERE Domain = ?'
                params = (domain_filter,)
            
            query += ' ORDER BY Control_ID'  # Add ordering
            df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            # Replace NaN values with empty strings
            df = df.fillna('')
            return df
        except Exception as e:
            print(f"Error getting controls: {str(e)}")
            return pd.DataFrame()
    
    def get_control_details(self, control_id):
        """Get details for a specific control"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT Control_ID, Domain, Control_Name, Control_Description, Implementation_Guidance FROM control_framework WHERE Control_ID = ?',
                (control_id,)
            )
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'Control_ID': row[0],
                    'Domain': row[1],
                    'Control_Name': row[2],
                    'Control_Description': row[3],
                    'Implementation_Guidance': row[4]
                }
            return None
        except Exception as e:
            print(f"Error getting control details: {str(e)}")
            return None
    
    def update_control(self, control_id: str, data: Dict) -> Tuple[bool, str]:
        """Update control information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE control_framework 
                SET Control_Name = ?,
                    Control_Description = ?,
                    Implementation_Guidance = ?
                WHERE Control_ID = ?
            ''', (
                data['Control_Name'],
                data['Control_Description'],
                data['Implementation_Guidance'],
                control_id
            ))
            conn.commit()
            conn.close()
            return True, "Control updated successfully"
        except Exception as e:
            return False, str(e)
    
    def validate_mapping(self, mapping):
        """Validate mapping data before saving"""
        if not mapping.get('framework_source'):
            return False, "Framework source is required"
        if not mapping.get('mapping_id'):
            return False, "Reference ID is required"
        # Add more validation as needed
        return True, ""
    
    def update_mappings(self, control_id, mappings):
        """Update control mappings"""
        try:
            # Convert mappings to the new format
            formatted_mappings = []
            for mapping in mappings:
                if mapping.get('framework_source') and mapping.get('mapping_id'):
                    formatted_text = f"{mapping['framework_source']}: {mapping['mapping_id']} - {mapping['description']}"
                    formatted_mappings.append(formatted_text)
            
            # Join with semicolons
            mapping_text = '; '.join(formatted_mappings)
            
            conn = self.get_connection()
            c = conn.cursor()
            
            # Update mapping text in control_framework
            c.execute('''
                UPDATE control_framework
                SET Mapping_to_Frameworks = ?
                WHERE Control_ID = ?
            ''', (mapping_text, control_id))
            
            # Update corresponding entries in as_mapping
            for mapping in mappings:
                if mapping.get('framework_source') and mapping.get('mapping_id'):
                    c.execute('''
                        INSERT OR REPLACE INTO as_mapping 
                        (framework, reference, requirement, mapping)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        mapping['framework_source'],
                        mapping['mapping_id'],
                        mapping['description'],
                        control_id
                    ))
            
            conn.commit()
            conn.close()
            return True, "Mappings updated successfully"
        except Exception as e:
            return False, str(e)
    
    def get_domains(self):
        """Get list of unique domains"""
        conn = self.get_connection()
        df = pd.read_sql('SELECT DISTINCT Domain FROM control_framework', conn)
        conn.close()
        return ["All Domains"] + sorted(df['Domain'].unique().tolist())
    
    def get_frameworks(self):
        """Get list of unique framework sources"""
        try:
            conn = self.get_connection()
            df = pd.read_sql('SELECT DISTINCT framework FROM as_mapping ORDER BY framework', conn)
            conn.close()
            return df['framework'].tolist()
        except Exception as e:
            print(f"Error getting frameworks: {str(e)}")
            return []
    
    def get_source_frameworks(self, control_id):
        """Get source frameworks for a control"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(
                'SELECT Mapping_to_Frameworks FROM control_framework WHERE Control_ID = ?',
                conn,
                params=(control_id,)
            )
            conn.close()
            
            if not df.empty and not pd.isna(df.iloc[0]['Mapping_to_Frameworks']):
                # Extract unique framework sources from mappings
                mappings = MappingProcessor.process_mapping_text(df.iloc[0]['Mapping_to_Frameworks'])
                sources = {m['framework_source'] for m in mappings if m.get('framework_source')}
                return sorted(sources)
            return []
        except Exception:
            return []
    
    def get_authoritative_sources(self, framework_source):
        """Get authoritative source references for a framework"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(
                'SELECT DISTINCT reference FROM as_mapping WHERE framework = ?',
                conn,
                params=(framework_source,)
            )
            conn.close()
            return sorted(df['reference'].unique().tolist())
        except Exception:
            return []
    
    def get_all_framework_sources(self):
        """Get all unique framework sources"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT framework FROM as_mapping')
            sources = [row[0] for row in cursor.fetchall()]
            conn.close()
            return sources
        except Exception as e:
            print(f"Error getting framework sources: {str(e)}")
            return []
    
    def get_all_authoritative_sources(self):
        """Get all authoritative source references with their requirements"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(
                'SELECT framework, reference, requirement FROM as_mapping',
                conn
            )
            conn.close()
            
            # Create a dictionary of reference: requirement pairs
            sources_dict = {}
            for _, row in df.iterrows():
                key = f"{row['framework']}.{row['reference']}" if row['framework'] else row['reference']
                sources_dict[key] = row['requirement']
            
            return {
                'references': sorted(sources_dict.keys()),
                'descriptions': sources_dict
            }
        except Exception:
            return {'references': [], 'descriptions': {}}
    
    def get_source_requirement(self, reference):
        """Get requirement text for a specific reference"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(
                'SELECT requirement FROM as_mapping WHERE reference = ?',
                conn,
                params=(reference,)
            )
            conn.close()
            return df.iloc[0]['requirement'] if not df.empty else ""
        except Exception:
            return ""
    
    def get_framework_references(self, framework):
        """Get all references for a framework"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'SELECT reference, requirement FROM as_mapping WHERE framework = ?',
                (framework,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            references = []
            descriptions = {}
            for row in rows:
                references.append(row[0])
                descriptions[row[0]] = row[1]
            
            return {
                'references': references,
                'descriptions': descriptions
            }
        except Exception as e:
            print(f"Error getting framework references: {str(e)}")
            return {'references': [], 'descriptions': {}}
    
    def get_reference_requirement(self, framework, reference):
        """Get requirement text for a specific framework reference"""
        try:
            conn = self.get_connection()
            df = pd.read_sql(
                'SELECT requirement FROM as_mapping WHERE framework = ? AND reference = ?',
                conn,
                params=(framework, reference)
            )
            conn.close()
            return df.iloc[0]['requirement'] if not df.empty else ""
        except Exception:
            return ""
    
    def get_mapping_details(self, framework, reference):
        """Get details for a specific mapping"""
        conn = self.get_connection()
        df = pd.read_sql(
            'SELECT * FROM as_mapping WHERE framework = ? AND reference = ?',
            conn,
            params=(framework, reference)
        )
        conn.close()
        return df.iloc[0] if not df.empty else None
    
    def update_mapping_details(self, framework, reference, data):
        """Update mapping details"""
        try:
            conn = self.get_connection()
            c = conn.cursor()
            c.execute('''
                UPDATE as_mapping
                SET requirement = ?,
                    classification = ?,
                    classification_justification = ?,
                    mapping = ?,
                    mapping_justification = ?
                WHERE framework = ? AND reference = ?
            ''', (
                data['requirement'],
                data['classification'],
                data['classification_justification'],
                data['mapping'],
                data['mapping_justification'],
                framework,
                reference
            ))
            conn.commit()
            conn.close()
            return True, "Mapping details saved successfully"
        except Exception as e:
            return False, str(e)
    
    def get_mappings(self, source_filter=None):
        """Get mappings with optional source filter"""
        conn = self.get_connection()
        query = 'SELECT * FROM as_mapping'
        if source_filter:
            query += ' WHERE framework = ?'
            df = pd.read_sql(query, conn, params=(source_filter,))
        else:
            df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    def search_mappings(self, search_term):
        """Search mappings based on search term"""
        if not search_term:
            return self.get_mappings()
        
        conn = self.get_connection()
        search_pattern = f"%{search_term}%"
        df = pd.read_sql('''
            SELECT * FROM as_mapping
            WHERE framework LIKE ? 
            OR reference LIKE ?
            OR requirement LIKE ?
            OR classification LIKE ?
        ''', conn, params=(search_pattern, search_pattern, search_pattern, search_pattern))
        conn.close()
        return df
    
    def get_mapping_data(self, source_filter=None):
        """Get mapping data with optional source filter"""
        try:
            conn = self.get_connection()
            if isinstance(source_filter, (list, set)):
                # Multiple sources
                if len(source_filter) > 0:
                    placeholders = ','.join('?' * len(source_filter))
                    query = f'SELECT * FROM as_mapping WHERE framework IN ({placeholders})'
                    df = pd.read_sql(query, conn, params=tuple(source_filter))
                else:
                    df = pd.read_sql('SELECT * FROM as_mapping', conn)
            elif source_filter:
                # Single source
                query = 'SELECT * FROM as_mapping WHERE framework = ?'
                df = pd.read_sql(query, conn, params=(source_filter,))
            else:
                # All sources
                df = pd.read_sql('SELECT * FROM as_mapping', conn)
            
            conn.close()
            
            # Replace NaN values with empty strings
            df = df.fillna('')
            
            # Sort by framework and reference
            if not df.empty:
                df = df.sort_values(['framework', 'reference'])
            
            return df
        except Exception as e:
            print(f"Error getting mapping data: {str(e)}")
            return pd.DataFrame()
    
    def get_reference_details(self, framework: str, reference: str) -> Dict:
        """Get details for a specific reference"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get all columns from as_mapping table
            cursor.execute('''
                SELECT * FROM as_mapping 
                WHERE framework = ? AND reference = ?
            ''', (framework, reference))
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Create a dictionary with all columns
                result = {}
                for i, column in enumerate(columns):
                    result[column] = row[i] if row[i] is not None else ''
                return result
            return None
        except Exception as e:
            print(f"Error getting reference details: {str(e)}")
            return None
    
    def update_as_reference(self, framework: str, reference: str, data: Dict) -> Tuple[bool, str]:
        """Update authoritative source reference information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE as_mapping 
                SET requirement = ?,
                    classification = ?,
                    classification_justification = ?,
                    mapping_justification = ?
                WHERE framework = ? AND reference = ?
            ''', (
                data['requirement'],
                data['classification'],
                data['classification_justification'],
                data['mapping_justification'],
                framework,
                reference
            ))
            conn.commit()
            conn.close()
            return True, "Reference updated successfully"
        except Exception as e:
            return False, str(e)
    
    def get_control_mappings(self, control_id):
        """Get all mappings for a specific control"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get mappings from as_mapping table
            cursor.execute('''
                SELECT framework as framework_source, 
                       reference, 
                       requirement 
                FROM as_mapping 
                WHERE control_ids LIKE ?
            ''', (f'%{control_id}%',))
            rows = cursor.fetchall()
            
            # Get mappings from control_framework table
            cursor.execute('''
                SELECT Mapping_to_Frameworks 
                FROM control_framework 
                WHERE Control_ID = ?
            ''', (control_id,))
            mapping_text = cursor.fetchone()
            
            conn.close()
            
            mappings = []
            
            # Process mappings from as_mapping table
            for row in rows:
                mappings.append({
                    'framework_source': row[0],
                    'reference': row[1],
                    'requirement': row[2]
                })
            
            # Process mappings from control_framework table if they exist
            if mapping_text and mapping_text[0]:
                mapping_entries = MappingProcessor.process_mapping_text(mapping_text[0])
                # Add any mappings that aren't already included
                for entry in mapping_entries:
                    if not any(m['framework_source'] == entry['framework_source'] and 
                             m['reference'] == entry['mapping_id'] for m in mappings):
                        mappings.append({
                            'framework_source': entry['framework_source'],
                            'reference': entry['mapping_id'],
                            'requirement': entry.get('description', '')
                        })
            
            return mappings
            
        except Exception as e:
            print(f"Error getting control mappings: {str(e)}")
            return []
    
    def add_control_mapping(self, control_id, framework, reference, requirement):
        """Add a new mapping for a control"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get existing control_ids for this mapping
            cursor.execute(
                'SELECT control_ids FROM as_mapping WHERE framework = ? AND reference = ?',
                (framework, reference)
            )
            result = cursor.fetchone()
            
            if result:
                existing_ids = set(result[0].split(';')) if result[0] else set()
                existing_ids.add(control_id)
                new_control_ids = ';'.join(existing_ids)
                
                # Update existing mapping
                cursor.execute('''
                    UPDATE as_mapping 
                    SET control_ids = ?
                    WHERE framework = ? AND reference = ?
                ''', (new_control_ids, framework, reference))
            else:
                # Insert new mapping
                cursor.execute('''
                    INSERT INTO as_mapping (framework, reference, requirement, control_ids)
                    VALUES (?, ?, ?, ?)
                ''', (framework, reference, requirement, control_id))
            
            conn.commit()
            conn.close()
            return True, "Mapping added successfully"
        except Exception as e:
            return False, str(e)
    
    def remove_control_mapping(self, control_id: str) -> bool:
        """Remove a control mapping completely"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Remove the mapping from control_framework
            cursor.execute('''
                UPDATE control_framework 
                SET Mapping_to_Frameworks = NULL
                WHERE Control_ID = ?
            ''', (control_id,))
            
            # Remove any associated mappings from as_mapping
            cursor.execute('''
                UPDATE as_mapping
                SET control_ids = REPLACE(control_ids, ?, '')
                WHERE control_ids LIKE ?
            ''', (control_id, f'%{control_id}%'))
            
            # Clean up any empty or malformed control_ids
            cursor.execute('''
                UPDATE as_mapping
                SET control_ids = NULL
                WHERE control_ids IN ('', ';', ';;')
            ''')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing control mapping: {str(e)}")
            return False
    
    def get_as_control_mappings(self, framework: str, reference: str) -> List[str]:
        """Get all control mappings for a specific reference"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT control_ids 
                FROM as_mapping 
                WHERE framework = ? AND reference = ?
            ''', (framework, reference))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0]:
                return result[0].split(';')
            return []
        except Exception as e:
            print(f"Error getting AS control mappings: {str(e)}")
            return []
    
    def get_all_controls(self) -> List[Dict]:
        """Get all controls for selection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT Control_ID, Control_Name FROM control_framework')
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {'Control_ID': row[0], 'Control_Name': row[1]}
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting all controls: {str(e)}")
            return []
    
    def add_as_control_mapping(self, framework: str, reference: str, control_id: str) -> Tuple[bool, str]:
        """Add a control mapping to an authoritative source reference"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get existing control_ids
            cursor.execute(
                'SELECT control_ids FROM as_mapping WHERE framework = ? AND reference = ?',
                (framework, reference)
            )
            result = cursor.fetchone()
            
            if result:
                existing_ids = set(result[0].split(';')) if result[0] else set()
                existing_ids.add(control_id)
                new_control_ids = ';'.join(existing_ids)
                
                # Update control_ids
                cursor.execute('''
                    UPDATE as_mapping 
                    SET control_ids = ?
                    WHERE framework = ? AND reference = ?
                ''', (new_control_ids, framework, reference))
                
                conn.commit()
                conn.close()
                return True, "Control mapping added successfully"
            return False, "Reference not found"
        except Exception as e:
            return False, str(e)
    
    def remove_as_control_mapping(self, framework: str, reference: str, control_id: str) -> Tuple[bool, str]:
        """Remove a control mapping from an authoritative source reference"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get existing control_ids
            cursor.execute(
                'SELECT control_ids FROM as_mapping WHERE framework = ? AND reference = ?',
                (framework, reference)
            )
            result = cursor.fetchone()
            
            if result and result[0]:
                existing_ids = set(result[0].split(';'))
                existing_ids.discard(control_id)
                
                # Update with remaining control IDs
                new_control_ids = ';'.join(existing_ids) if existing_ids else None
                cursor.execute('''
                    UPDATE as_mapping 
                    SET control_ids = ?
                    WHERE framework = ? AND reference = ?
                ''', (new_control_ids, framework, reference))
                
                conn.commit()
                conn.close()
                return True, "Control mapping removed successfully"
            return False, "No mappings found"
        except Exception as e:
            return False, str(e)
    
    def remove_mappings(self, mapping_ids):
        """Remove multiple mappings by their IDs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete mappings
            cursor.executemany(
                "DELETE FROM control_mappings WHERE id = ?",
                [(mapping_id,) for mapping_id in mapping_ids]
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing mappings: {str(e)}")
            return False

class MappingProcessor:
    @staticmethod
    def process_mapping_text(text):
        """Process mapping text into structured format"""
        if pd.isna(text):
            return []
        
        mappings = []
        
        # Split by semicolon to get individual mappings
        mapping_texts = [m.strip() for m in str(text).split(';') if m.strip()]
        
        for mapping_text in mapping_texts:
            try:
                # Split into framework:reference - requirement
                if ':' not in mapping_text or '-' not in mapping_text:
                    continue
                    
                framework_ref, requirement = mapping_text.split('-', 1)
                framework_ref = framework_ref.strip()
                
                if ':' in framework_ref:
                    framework_source, mapping_id = framework_ref.split(':', 1)
                    mappings.append({
                        'mapping_id': mapping_id.strip(),
                        'framework_source': framework_source.strip(),
                        'description': requirement.strip()
                    })
            except Exception:
                continue
        
        return mappings
    
    @staticmethod
    def get_framework_sources(control_id, db):
        """Get unique framework sources for a control"""
        return db.get_source_frameworks(control_id)
