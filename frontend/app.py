import streamlit as st
from utils import login, get_current_user
import os

# Page config
st.set_page_config(
    page_title="Library System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_welcome_page()

def show_login_page():
    st.title("📚 School Library System")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Sign In")
            
            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        token_data = login(username, password)
                        if token_data:
                            st.session_state.token = token_data["access_token"]
                            user_info = get_current_user(token_data["access_token"])
                            if user_info:
                                st.session_state.authenticated = True
                                st.session_state.user = user_info
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Failed to get user info")
                        else:
                            st.error("Invalid username or password")

def show_welcome_page():
    st.title(f"Welcome, {st.session_state.user['username']}!")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    Select a page from the sidebar to manage the library:
    
    - **📊 Dashboard**: View book inventory and status
    - **🔍 Search**: Find books and check availability
    - **⚙️ Admin**: Manage teachers and system settings
    """)
    
    # Quick Stats (Placeholder until we fetch real data)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("👈 Use the sidebar to navigate")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

if __name__ == "__main__":
    main()
