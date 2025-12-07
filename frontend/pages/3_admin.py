import streamlit as st
import pandas as pd
from utils import fetch_data, post_data

st.set_page_config(page_title="Admin", page_icon="⚙️", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login first.")
    st.stop()

# Check if user is admin (optional, backend enforces it too)
if st.session_state.user.get('role') != 'admin':
    st.error("Access Denied. Admin privileges required.")
    st.stop()

st.title("⚙️ Admin Panel")

tab1, tab2, tab3 = st.tabs(["👥 Teachers", "📚 Books", "🏷️ Categories"])

# --- Teachers Management ---
with tab1:
    st.header("Manage Teachers")
    
    # Add Teacher Form
    with st.expander("➕ Add New Teacher"):
        with st.form("add_teacher"):
            t_name = st.text_input("Teacher Name")
            t_classroom = st.text_input("Classroom")
            submitted = st.form_submit_button("Add Teacher")
            
            if submitted:
                if t_name:
                    resp = post_data("teachers/", st.session_state.token, {"name": t_name, "classroom": t_classroom})
                    if resp and resp.status_code == 201:
                        st.success("Teacher added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add teacher.")
                else:
                    st.warning("Name is required.")

    # List Teachers
    teachers = fetch_data("teachers/", st.session_state.token)
    if teachers:
        st.dataframe(pd.DataFrame(teachers), use_container_width=True, hide_index=True)
    else:
        st.info("No teachers found.")

# --- Books Management ---
with tab2:
    st.header("Manage Books")
    st.info("Bulk import books via CSV using the ETL pipeline. Use this form for single entries.")
    
    with st.expander("➕ Add Single Book"):
        with st.form("add_book"):
            b_id = st.text_input("Book ID (e.g., A-001)")
            b_title = st.text_input("Book Title")
            # Ideally fetch categories and locations for dropdowns
            # For simplicity now, using text/number inputs or placeholders
            b_cat_id = st.number_input("Category ID", min_value=1, step=1)
            b_loc_id = st.number_input("Location ID", min_value=1, step=1)
            
            submitted_b = st.form_submit_button("Add Book")
            
            if submitted_b:
                if b_id and b_title:
                    payload = {
                        "book_id": b_id,
                        "name": b_title,
                        "category_id": int(b_cat_id),
                        "storage_location_id": int(b_loc_id)
                    }
                    resp = post_data("books/", st.session_state.token, payload)
                    if resp and resp.status_code == 201:
                        st.success("Book added successfully!")
                    else:
                        st.error(f"Failed to add book. {resp.text if resp else ''}")
                else:
                    st.warning("ID and Title are required.")

# --- Categories Management ---
with tab3:
    st.header("System Categories")
    st.info("Categories are managed via the database initialization or ETL process.")
    # Just display them for now
    # categories = fetch_data("categories/", st.session_state.token) # Endpoint might not exist yet in my router list, let's check
    # I didn't explicitly create a categories router in the backend setup step.
    # I should probably add one or just skip this for now.
    st.write("Category management coming soon.")
