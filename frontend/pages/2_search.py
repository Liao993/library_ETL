import streamlit as st
import pandas as pd
from utils import fetch_data

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login first.")
    st.stop()

st.title("🔍 Book Search")

# Search Input
book_id_query = st.text_input("Enter Book ID (e.g., A-018)", help="Type the exact Book ID found on the label")

if book_id_query:
    with st.spinner("Searching..."):
        # Fetch book details
        try:
            book = fetch_data(f"books/{book_id_query}", st.session_state.token)
            
            if book:
                st.success(f"Book Found: {book['name']}")
                
                # Display Book Details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📖 Book Details")
                    st.write(f"**ID:** {book['book_id']}")
                    st.write(f"**Title:** {book['name']}")
                    st.write(f"**Status:** {book['status']}")
                    
                    # Status Badge
                    if book['status'] == 'Available':
                        st.success("Available")
                    elif book['status'] == 'On Loan':
                        st.warning("On Loan")
                    elif book['status'] == 'Lost':
                        st.error("Lost")
                    else:
                        st.info(book['status'])

                with col2:
                    st.markdown("### 📍 Location Info")
                    # We might need to fetch category/location details if not fully expanded in book response
                    # For now, just showing IDs
                    st.write(f"**Category ID:** {book['category_id']}")
                    st.write(f"**Location ID:** {book['storage_location_id']}")
                    st.write(f"**Last Updated:** {book['updated_at']}")

                # Transaction History for this book
                st.markdown("### 📜 Transaction History")
                transactions = fetch_data("transactions/", st.session_state.token, params={"book_id": book_id_query})
                
                if transactions:
                    df_trans = pd.DataFrame(transactions)
                    st.dataframe(
                        df_trans[['transaction_date', 'action', 'teacher_id', 'timestamp']],
                        column_config={
                            "transaction_date": "Date",
                            "action": "Action",
                            "teacher_id": "Teacher ID",
                            "timestamp": "Time"
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No transaction history found for this book.")
            
            else:
                st.error(f"Book with ID '{book_id_query}' not found.")
                
        except Exception as e:
            st.error(f"Error occurred: {e}")
