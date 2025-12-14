import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_data

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login first.")
    st.stop()

st.title("📊圖書管理系統")

# Fetch data
with st.spinner("Loading data..."):
    try:
        stats = fetch_data("books/stats", st.session_state.token)
        # Still fetch books for the table/chart, maybe with pagination later
        books = fetch_data("books/", st.session_state.token, params={"limit": 1000}) 
        transactions = fetch_data("transactions/", st.session_state.token, params={"limit": 10})
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        st.stop()

# Display Metrics from Backend
if stats:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("總書籍", stats.get('total_books', 0))
    col2.metric("可借閱", stats.get('available_books', 0))
    col3.metric("不可借閱", stats.get('not_available_books', 0))
    col4.metric("捐贈", stats.get('donation_books', 0))
    col5.metric("自購", stats.get('self_bought_books', 0))
   
    



    df_books = pd.DataFrame(books)
    
    # Extract location name from nested storage_location object
    df_books['location_name'] = df_books['storage_location'].apply(
        lambda x: x.get('location_name', '未設定') if isinstance(x, dict) and x else '未設定'
    )
    
    # Inventory Table
    st.subheader("進階搜尋")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Get unique statuses and sort them
        all_statuses = sorted(df_books['status'].unique().tolist())
        
        # Select All checkbox for status
        select_all_status = st.checkbox("全選狀態", value=True, key="select_all_status")
        
        if select_all_status:
            status_filter = st.multiselect(
                "狀態", 
                options=all_statuses, 
                default=all_statuses,
                key="status_multiselect"
            )
        else:
            status_filter = st.multiselect(
                "狀態", 
                options=all_statuses, 
                default=[],
                key="status_multiselect_2"
            )
    
    with col2:
        # Get unique locations and sort them
        all_locations = sorted(df_books['location_name'].unique().tolist())
        
        # Select All checkbox for location
        select_all_location = st.checkbox("全選位置", value=True, key="select_all_location")
        
        if select_all_location:
            location_filter = st.multiselect(
                "位置", 
                options=all_locations, 
                default=all_locations,
                key="location_multiselect"
            )
        else:
            location_filter = st.multiselect(
                "位置", 
                options=all_locations, 
                default=[],
                key="location_multiselect_2"
            )
    
    # Apply filters
    filtered_df = df_books[
        (df_books['status'].isin(status_filter)) & 
        (df_books['location_name'].isin(location_filter))
    ]
    
    # Sort by book_category_label and then location_name
    filtered_df = filtered_df.sort_values(by=['location_name', 'book_category_label'])
    
    # Select and reorder columns for display
    display_columns = ['book_category', 'book_category_label', 'name', 'status', 'location_name']
    display_df = filtered_df[display_columns].copy()
    
    st.dataframe(
        display_df,
        column_config={
            "book_category": "類別",
            "book_category_label": "類別標籤",
            "name": "書名",
            "status": "狀態",
            "location_name": "位置"
        },
        use_container_width=True,
        hide_index=True
    )
    
    # CSV Export
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 下載 CSV",
        data=csv,
        file_name="book_inventory.csv",
        mime="text/csv",
    )

else:
    st.info("資料庫中沒有找到書籍。請透過管理面板或 ETL 流程新增書籍。")

# Recent Transactions
st.subheader("借閱紀錄")
if transactions:
    df_trans = pd.DataFrame(transactions)
    st.dataframe(
        df_trans,
        column_config={
            "transaction_id": "交易ID",
            "book_id": "書籍ID",
            "teacher_id": "教師ID",
            "action": "動作",
            "transaction_date": "日期",
            "timestamp": "時間戳記"
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("目前沒有借閱紀錄")
