import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_data

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login first.")
    st.stop()

st.title("📊 Library Dashboard")

# Fetch data
with st.spinner("Loading data..."):
    books = fetch_data("books/", st.session_state.token, params={"limit": 1000})
    transactions = fetch_data("transactions/", st.session_state.token, params={"limit": 1000})

if books:
    df_books = pd.DataFrame(books)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_books = len(df_books)
    available_books = len(df_books[df_books['status'] == 'Available'])
    on_loan_books = len(df_books[df_books['status'] == 'On Loan'])
    lost_books = len(df_books[df_books['status'] == 'Lost'])
    
    col1.metric("Total Books", total_books)
    col2.metric("Available", available_books)
    col3.metric("On Loan", on_loan_books)
    col4.metric("Lost/Archived", lost_books + len(df_books[df_books['status'] == 'Archived']))
    
    # Charts
    st.subheader("Book Status Distribution")
    if not df_books.empty:
        status_counts = df_books['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig = px.pie(status_counts, values='Count', names='Status', title='Book Status')
        st.plotly_chart(fig, use_container_width=True)
    
    # Inventory Table
    st.subheader("Book Inventory")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect("Filter by Status", options=df_books['status'].unique(), default=df_books['status'].unique())
    
    filtered_df = df_books[df_books['status'].isin(status_filter)]
    
    st.dataframe(
        filtered_df,
        column_config={
            "book_id": "Book ID",
            "name": "Title",
            "status": "Status",
            "category_id": "Category ID",
            "storage_location_id": "Location ID",
            "updated_at": "Last Updated"
        },
        use_container_width=True,
        hide_index=True
    )
    
    # CSV Export
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Inventory CSV",
        data=csv,
        file_name="book_inventory.csv",
        mime="text/csv",
    )

else:
    st.info("No books found in the database. Add some books via the Admin panel or ETL process.")

# Recent Transactions
st.subheader("Recent Transactions")
if transactions:
    df_trans = pd.DataFrame(transactions)
    st.dataframe(
        df_trans,
        column_config={
            "transaction_id": "ID",
            "book_id": "Book ID",
            "teacher_id": "Teacher ID",
            "action": "Action",
            "transaction_date": "Date",
            "timestamp": "Timestamp"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No recent transactions.")
