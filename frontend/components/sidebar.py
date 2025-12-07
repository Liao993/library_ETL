import streamlit as st

def sidebar():
    with st.sidebar:
        st.title("Library System")
        if st.session_state.get("authenticated"):
            st.write(f"Logged in as: **{st.session_state.user['username']}**")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
        else:
            st.info("Please log in to access the system.")
