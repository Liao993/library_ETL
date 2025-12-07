import requests
import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

def login(username, password):
    """Login to the API and return the access token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API. Is it running?")
        return None

def get_current_user(token):
    """Get current user details."""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_data(endpoint, token, params=None):
    """Generic function to fetch data from API."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.session_state.authenticated = False
            st.rerun()
        else:
            st.error(f"Error fetching data: {response.text}")
            return []
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

def post_data(endpoint, token, data):
    """Generic function to post data to API."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}", headers=headers, json=data)
        return response
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def put_data(endpoint, token, data):
    """Generic function to put (update) data to API."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.put(f"{API_BASE_URL}/{endpoint}", headers=headers, json=data)
        return response
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None
