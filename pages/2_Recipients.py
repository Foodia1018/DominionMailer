import streamlit as st
import pandas as pd
import io
from utils import Helpers

st.set_page_config(
    page_title="Recipients | DominionMailer",
    page_icon="👥",
    layout="wide"
)

# Check if database is initialized
if "db" not in st.session_state:
    st.error("Database not initialized. Please restart the application.")
    st.stop()

db = st.session_state.db

# Initialize session state variables
if "recipient_list_id" not in st.session_state:
    st.session_state.recipient_list_id = None

if "recipient_view" not in st.session_state:
    st.session_state.recipient_view = "list"  # list, create, edit, import

# Header
st.title("👥 Recipient Management")

# Sidebar with list selection
st.sidebar.header("Recipient Lists")

# Create new list button
if st.sidebar.button("➕ Create New List"):
    st.session_state.recipient_view = "create_list"
    st.rerun()

# Get all recipient lists
recipient_lists = db.get_recipient_lists()

if recipient_lists and len(recipient_lists) > 0:
    # Format options for selectbox
    list_options = [(rl['id'], rl['name']) for rl in recipient_lists]
    
    selected_list_id = st.sidebar.selectbox(
        "Select a list to manage:",
        options=[rl[0] for rl in list_options],
        format_func=lambda x: next((rl[1] for rl in list_options if rl[0] == x), ""),
        key="recipient_list_select"
    )
    
    # Set the selected list in session state
    st.session_state.recipient_list_id = selected_list_id
    
    # List actions
    st.sidebar.markdown("---")
    st.sidebar.subheader("List Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Rename", key="rename_list"):
            st.session_state.recipient_view = "rename_list"
            st.rerun()
    
    with col2:
        if st.button("❌ Delete", key="delete_list"):
            st.session_state.recipient_view = "delete_list"
            st.rerun()
    
    # Import buttons
    if st.sidebar.button("📥 Import Recipients from CSV", key="import_csv"):
        st.session_state.recipient_view = "import"
        st.rerun()
else:
    st.sidebar.info("No recipient lists found. Create your first list using the button above.")

# Main content area
if st.session_state.recipient_view == "list" and st.session_state.recipient_list_id:
    # Show recipients in the selected list
    selected_list = db.get_recipient_list_by_id(st.session_state.recipient_list_id)
    
    if selected_list:
        st.subheader(f"Recipients in list: {selected_list['name']}")
        
        # Add new recipient button
        if st.button("➕ Add New Recipient", key="add_recipient"):
            st.session_state.recipient_view = "add_recipient"
            st.rerun()
        
        # Get recipients in this list
        recipients = db.get_recipients_by_list(st.session_state.recipient_list_id)
        
        if recipients and len(recipients) > 0:
            # Convert to DataFrame for display
            recipients_df = pd.DataFrame([dict(r) for r in recipients])
            
            # Select which columns to display
            display_cols = ['id', 'email', 'name', 'status', 'added_at']
            display_cols = [col for col in display_cols if col in recipients_df.columns]
            
            # Add custom columns if data exists
            custom_cols = ['custom1', 'custom2', 'custom3', 'custom4', 'custom5']
            for col in custom_cols:
                if col in recipients_df.columns and not recipients_df[col].isna().all():
                    display_cols.append(col)
            
            # Create dataframe with selected columns
            st.dataframe(
                recipients_df[display_cols],
                column_config={
                    "id": st.column_config.NumberColumn("ID"),
                    "email": st.column_config.TextColumn("Email"),
                    "name": st.column_config.TextColumn("Name"),
                    "status": st.column_config.TextColumn("Status"),
                    "added_at": st.column_config.DatetimeColumn("Added"),
                    "custom1": st.column_config.TextColumn("Custom 1"),
                    "custom2": st.column_config.TextColumn("Custom 2"),
                    "custom3": st.column_config.TextColumn("Custom 3"),
                    "custom4": st.column_config.TextColumn("Custom 4"),
                    "custom5": st.column_config.TextColumn("Custom 5"),
                },
                hide_index=True
            )
            
            # Export option
            if st.button("📤 Export to CSV", key="export_csv"):
                csv = recipients_df[display_cols].to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_list['name']}_recipients.csv",
                    mime="text/csv"
                )
        else:
            st.info("No recipients in this list. Add recipients using the buttons above.")
    else:
        st.error("Selected list not found. Please select another list.")

elif st.session_state.recipient_view == "create_list":
    # Form to create a new recipient list
    st.subheader("Create New Recipient List")
    
    with st.form("create_list_form"):
        list_name = st.text_input("List Name", placeholder="Newsletter Subscribers")
        submit_button = st.form_submit_button("Create List")
        
        if submit_button:
            if not list_name:
                st.error("List name is required.")
            else:
                try:
                    new_list_id = db.add_recipient_list(list_name)
                    if new_list_id:
                        st.success(f"List '{list_name}' created successfully!")
                        # Set the new list as selected
                        st.session_state.recipient_list_id = new_list_id
                        st.session_state.recipient_view = "list"
                        st.rerun()
                    else:
                        st.error("Failed to create list. Please try again.")
                except Exception as e:
                    st.error(f"Error creating list: {str(e)}")
    
    # Cancel button
    if st.button("Cancel", key="cancel_create_list"):
        st.session_state.recipient_view = "list"
        st.rerun()

elif st.session_state.recipient_view == "rename_list" and st.session_state.recipient_list_id:
    # Form to rename an existing list
    selected_list = db.get_recipient_list_by_id(st.session_state.recipient_list_id)
    
    if selected_list:
        st.subheader(f"Rename List: {selected_list['name']}")
        
        with st.form("rename_list_form"):
            new_name = st.text_input("New List Name", value=selected_list['name'])
            submit_button = st.form_submit_button("Rename List")
            
            if submit_button:
                if not new_name:
                    st.error("List name is required.")
                else:
                    try:
                        # This method doesn't exist in our DB class, so we'd need to add it
                        # For now, let's simulate it with an execute_query call
                        db.execute_query(
                            "UPDATE recipient_lists SET name = ? WHERE id = ?",
                            (new_name, st.session_state.recipient_list_id),
                            commit=True
                        )
                        st.success(f"List renamed to '{new_name}' successfully!")
                        st.session_state.recipient_view = "list"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error renaming list: {str(e)}")
        
        # Cancel button
        if st.button("Cancel", key="cancel_rename"):
            st.session_state.recipient_view = "list"
            st.rerun()
    else:
        st.error("Selected list not found. Please select another list.")

elif st.session_state.recipient_view == "delete_list" and st.session_state.recipient_list_id:
    # Confirmation for deleting a list
    selected_list = db.get_recipient_list_by_id(st.session_state.recipient_list_id)
    
    if selected_list:
        st.subheader(f"Delete List: {selected_list['name']}")
        
        st.warning(
            f"Are you sure you want to delete the list '{selected_list['name']}'? "
            "This will permanently delete all recipients in this list."
        )
        
        # Get recipient count
        recipients = db.get_recipients_by_list(st.session_state.recipient_list_id)
        recipient_count = len(recipients) if recipients else 0
        
        st.info(f"This list contains {recipient_count} recipients.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Yes, Delete List", key="confirm_delete_list"):
                try:
                    db.delete_recipient_list(st.session_state.recipient_list_id)
                    st.success("List deleted successfully!")
                    st.session_state.recipient_list_id = None
                    st.session_state.recipient_view = "list"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting list: {str(e)}")
        
        with col2:
            if st.button("Cancel", key="cancel_delete"):
                st.session_state.recipient_view = "list"
                st.rerun()
    else:
        st.error("Selected list not found. Please select another list.")

elif st.session_state.recipient_view == "add_recipient" and st.session_state.recipient_list_id:
    # Form to add a new recipient
    selected_list = db.get_recipient_list_by_id(st.session_state.recipient_list_id)
    
    if selected_list:
        st.subheader(f"Add Recipient to: {selected_list['name']}")
        
        with st.form("add_recipient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email Address", placeholder="user@example.com")
                name = st.text_input("Name", placeholder="John Doe")
            
            with col2:
                custom1 = st.text_input("Custom Field 1", placeholder="e.g., Company")
                custom2 = st.text_input("Custom Field 2", placeholder="e.g., Job Title")
            
            submit_button = st.form_submit_button("Add Recipient")
            
            if submit_button:
                if not email:
                    st.error("Email address is required.")
                elif not Helpers.is_valid_email(email):
                    st.error("Please enter a valid email address.")
                else:
                    try:
                        # Extract domain from email
                        domain = Helpers.extract_domain(email)
                        
                        # Add the recipient
                        new_recipient_id = db.add_recipient(
                            list_id=st.session_state.recipient_list_id,
                            email=email,
                            name=name or None,
                            domain=domain,
                            custom1=custom1 or None,
                            custom2=custom2 or None
                        )
                        
                        if new_recipient_id:
                            st.success(f"Recipient '{email}' added successfully!")
                            # Clear the form
                            st.session_state.recipient_view = "list"
                            st.rerun()
                        else:
                            st.error("Failed to add recipient. Please try again.")
                    except Exception as e:
                        st.error(f"Error adding recipient: {str(e)}")
        
        # Cancel button
        if st.button("Cancel", key="cancel_add"):
            st.session_state.recipient_view = "list"
            st.rerun()
    else:
        st.error("Selected list not found. Please select another list.")

elif st.session_state.recipient_view == "import" and st.session_state.recipient_list_id:
    # Import recipients from CSV
    selected_list = db.get_recipient_list_by_id(st.session_state.recipient_list_id)
    
    if selected_list:
        st.subheader(f"Import Recipients to: {selected_list['name']}")
        
        st.info(
            "Upload a CSV file with your recipients. The file must contain at least an 'email' column. "
            "Other recognized columns: 'name', 'custom1', 'custom2', 'custom3', 'custom4', 'custom5'."
        )
        
        # File uploader
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        
        if uploaded_file is not None:
            # Read CSV file
            try:
                df = pd.read_csv(uploaded_file)
                
                # Check if dataframe is empty
                if df.empty:
                    st.error("The uploaded CSV file is empty.")
                else:
                    # Preview the data
                    st.subheader("Data Preview")
                    st.dataframe(df.head(5))
                    
                    # Validate and process the data
                    valid, result = Helpers.validate_and_process_csv(df)
                    
                    if valid:
                        st.success(f"Found {len(result)} valid recipients in the CSV.")
                        
                        # Import options
                        st.subheader("Import Options")
                        
                        duplicate_action = st.radio(
                            "How to handle duplicate emails?",
                            ["Skip", "Update"],
                            index=0,
                            help="What to do if an email already exists in the list"
                        )
                        
                        # Import button
                        if st.button("Import Recipients", key="confirm_import"):
                            with st.spinner(f"Importing {len(result)} recipients..."):
                                imported_count = 0
                                skipped_count = 0
                                updated_count = 0
                                error_count = 0
                                
                                for recipient in result:
                                    try:
                                        # Check if email already exists in this list
                                        existing = db.execute_query(
                                            "SELECT id FROM recipients WHERE list_id = ? AND email = ?",
                                            (st.session_state.recipient_list_id, recipient['email']),
                                            fetch_one=True
                                        )
                                        
                                        if existing:
                                            if duplicate_action == "Skip":
                                                skipped_count += 1
                                            else:  # Update
                                                # Build update query based on available fields
                                                fields_to_update = {}
                                                for field in ['name', 'domain', 'custom1', 'custom2', 'custom3', 'custom4', 'custom5']:
                                                    if field in recipient and recipient[field] is not None:
                                                        fields_to_update[field] = recipient[field]
                                                
                                                if fields_to_update:
                                                    # Update the recipient
                                                    set_clause = ", ".join([f"{key} = ?" for key in fields_to_update.keys()])
                                                    query = f"UPDATE recipients SET {set_clause} WHERE id = ?"
                                                    
                                                    params = list(fields_to_update.values())
                                                    params.append(existing['id'])
                                                    
                                                    db.execute_query(query, params, commit=True)
                                                    updated_count += 1
                                        else:
                                            # Add new recipient
                                            db.add_recipient(
                                                list_id=st.session_state.recipient_list_id,
                                                email=recipient['email'],
                                                name=recipient.get('name'),
                                                domain=recipient.get('domain'),
                                                custom1=recipient.get('custom1'),
                                                custom2=recipient.get('custom2'),
                                                custom3=recipient.get('custom3'),
                                                custom4=recipient.get('custom4'),
                                                custom5=recipient.get('custom5')
                                            )
                                            imported_count += 1
                                    except Exception as e:
                                        error_count += 1
                            
                            # Show import results
                            st.success(f"Import completed with {imported_count} new recipients added.")
                            
                            if updated_count > 0:
                                st.info(f"{updated_count} existing recipients were updated.")
                            
                            if skipped_count > 0:
                                st.info(f"{skipped_count} duplicates were skipped.")
                            
                            if error_count > 0:
                                st.warning(f"{error_count} recipients could not be imported due to errors.")
                            
                            # Return to list view
                            if st.button("Back to List", key="back_after_import"):
                                st.session_state.recipient_view = "list"
                                st.rerun()
                    else:
                        # Display validation errors
                        st.error("CSV validation failed:")
                        st.error(result)
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
        
        # Sample CSV template
        st.markdown("### Need a template?")
        st.write("Download a sample CSV template to get started:")
        
        # Create a sample CSV
        sample_df = pd.DataFrame({
            'email': ['user1@example.com', 'user2@example.com'],
            'name': ['User One', 'User Two'],
            'custom1': ['Company A', 'Company B'],
            'custom2': ['Manager', 'Director']
        })
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        sample_df.to_csv(csv_buffer, index=False)
        
        # Download button
        st.download_button(
            label="Download Template CSV",
            data=csv_buffer.getvalue(),
            file_name="recipient_template.csv",
            mime="text/csv"
        )
        
        # Cancel button
        if st.button("Cancel Import", key="cancel_import"):
            st.session_state.recipient_view = "list"
            st.rerun()
    else:
        st.error("Selected list not found. Please select another list.")


# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *Design like a creator. Deliver like a machine.*")
