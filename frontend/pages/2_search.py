import streamlit as st
import pandas as pd
from utils import fetch_data

st.set_page_config(page_title="搜尋", page_icon="🔍", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("請先登入")
    st.stop()

st.title("🔍 書籍搜尋")

# Fetch all books
with st.spinner("載入資料中..."):
    try:
        books = fetch_data("books/", st.session_state.token, params={"limit": 1000})
    except Exception as e:
        st.error(f"無法載入資料: {e}")
        st.stop()

if not books:
    st.info("資料庫中沒有找到書籍")
    st.stop()

# Convert to DataFrame
df_books = pd.DataFrame(books)

# Extract location name from nested storage_location object
df_books['location_name'] = df_books['storage_location'].apply(
    lambda x: x.get('location_name', '未設定') if isinstance(x, dict) and x else '未設定'
)

# Search Section
st.subheader("搜尋條件")

col1, col2, col3 = st.columns(3)

with col1:
    # Category selectbox - get unique categories
    all_categories = ['全部'] + sorted(df_books['book_category'].unique().tolist())
    selected_category = st.selectbox("類別", options=all_categories, index=0)

with col2:
    # Category label text input
    category_label_input = st.text_input(
        "類別標籤", 
        placeholder="例如: B-009",
        help="輸入類別標籤進行搜尋，例如: B-009"
    )

with col3:
    # Book name text input
    name_input = st.text_input(
        "書名",
        placeholder="輸入書名關鍵字",
        help="輸入書名的部分或全部文字進行搜尋"
    )

# Apply filters
filtered_df = df_books.copy()

# Filter by category if not "全部"
if selected_category != '全部':
    filtered_df = filtered_df[filtered_df['book_category'] == selected_category]

# Filter by category_label if input provided
if category_label_input:
    filtered_df = filtered_df[
        filtered_df['book_category_label'].str.contains(category_label_input, case=False, na=False)
    ]

# Filter by name if input provided
if name_input:
    filtered_df = filtered_df[
        filtered_df['name'].str.contains(name_input, case=False, na=False)
    ]

# Sort by location_name and then book_category_label
filtered_df = filtered_df.sort_values(by=['location_name', 'book_category_label'])

# Display results
st.subheader(f"搜尋結果 ({len(filtered_df)} 本書)")

if len(filtered_df) > 0:
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
        label="📥 下載搜尋結果 CSV",
        data=csv,
        file_name="search_results.csv",
        mime="text/csv",
    )
else:
    st.info("沒有找到符合條件的書籍")

# Show search tips
with st.expander("💡 搜尋提示"):
    st.markdown("""
    **如何使用搜尋功能:**
    
    1. **類別搜尋**: 從下拉選單選擇特定類別（捐贈、自購、代管）
    2. **類別標籤搜尋**: 輸入標籤編號，例如 "B-009" 或 "代管B-001"
    3. **書名搜尋**: 輸入書名的任何部分，系統會自動找出包含該文字的所有書籍
    4. **組合搜尋**: 可以同時使用多個條件進行精確搜尋,但是標籤同時使用可能會衝突
    
    **範例:**
    - 搜尋所有代管類別的書: 選擇「代管」
    - 搜尋特定編號: 在類別標籤輸入 "B-009"
    - 搜尋書名包含「小熊」的書: 在書名輸入 "小熊"
    """)
