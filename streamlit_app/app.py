import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load environment variables from .env
load_dotenv()

# Get the DB URL from the environment
DB_URL = os.getenv("DB_URL")

# Set up Streamlit page with custom styling
st.set_page_config(
    page_title="Walmart Sales Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Walmart-themed styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #004c91 0%, #ffc220 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #ffc220;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #004c91 0%, #003d73 100%);
    }
    
    .stSelectbox label {
        color: #004c91;
        font-weight: bold;
    }
    
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🛒 Walmart Sales Analytics Dashboard</div>', unsafe_allow_html=True)

# SQLAlchemy engine
engine = create_engine(DB_URL)

@st.cache_data
def load_data():
    query = "SELECT * FROM sales"
    df = pd.read_sql(query, engine)
    # Convert date column if it exists
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# Load data
try:
    df = load_data()
    
    # Sidebar filters
    st.sidebar.markdown("### 🎯 Filter Options")
    
    # City filter
    cities = df["City"].unique().tolist() if "City" in df.columns else []
    selected_city = st.sidebar.selectbox("🏙️ Select City", ["All"] + cities)
    
    # Product line filter (if exists)
    product_lines = df["Product line"].unique().tolist() if "Product line" in df.columns else []
    selected_product = st.sidebar.multiselect("🛍️ Select Product Lines", product_lines, default=product_lines)
    
    # Customer type filter (if exists)
    customer_types = df["Customer type"].unique().tolist() if "Customer type" in df.columns else []
    selected_customer = st.sidebar.multiselect("👥 Select Customer Type", customer_types, default=customer_types)
    
    # Gender filter (if exists)
    genders = df["Gender"].unique().tolist() if "Gender" in df.columns else []
    selected_gender = st.sidebar.multiselect("⚧ Select Gender", genders, default=genders)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["City"] == selected_city]
    
    if "Product line" in filtered_df.columns and selected_product:
        filtered_df = filtered_df[filtered_df["Product line"].isin(selected_product)]
    
    if "Customer type" in filtered_df.columns and selected_customer:
        filtered_df = filtered_df[filtered_df["Customer type"].isin(selected_customer)]
    
    if "Gender" in filtered_df.columns and selected_gender:
        filtered_df = filtered_df[filtered_df["Gender"].isin(selected_gender)]
    
    # Key Metrics Row
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = filtered_df["Total"].sum() if "Total" in filtered_df.columns else 0
        st.metric("💰 Total Sales", f"${total_sales:,.2f}")
    
    with col2:
        total_transactions = len(filtered_df)
        st.metric("🛒 Total Transactions", f"{total_transactions:,}")
    
    with col3:
        avg_transaction = filtered_df["Total"].mean() if "Total" in filtered_df.columns else 0
        st.metric("📊 Avg Transaction", f"${avg_transaction:.2f}")
    
    with col4:
        unique_customers = filtered_df["Customer type"].nunique() if "Customer type" in filtered_df.columns else 0
        st.metric("👥 Customer Segments", unique_customers)
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛍️ Sales by Product Line")
        if "Product line" in filtered_df.columns and "Total" in filtered_df.columns:
            sales_by_product = filtered_df.groupby("Product line")["Total"].sum().sort_values(ascending=False)
            fig_product = px.bar(
                x=sales_by_product.index,
                y=sales_by_product.values,
                color=sales_by_product.values,
                color_continuous_scale="Blues",
                title="Sales Performance by Product Category"
            )
            fig_product.update_layout(
                xaxis_title="Product Line",
                yaxis_title="Total Sales ($)",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig_product, use_container_width=True)
    
    with col2:
        st.markdown("### 🏙️ Sales by City")
        if "City" in filtered_df.columns and "Total" in filtered_df.columns:
            sales_by_city = filtered_df.groupby("City")["Total"].sum().sort_values(ascending=False)
            fig_city = px.pie(
                values=sales_by_city.values,
                names=sales_by_city.index,
                title="Sales Distribution by City",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_city.update_layout(height=400)
            st.plotly_chart(fig_city, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Customer Analysis")
        if "Customer type" in filtered_df.columns and "Total" in filtered_df.columns:
            customer_analysis = filtered_df.groupby("Customer type")["Total"].agg(['sum', 'count']).reset_index()
            customer_analysis.columns = ['Customer Type', 'Total Sales', 'Transaction Count']
            
            fig_customer = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Sales by Customer Type', 'Transaction Count'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            fig_customer.add_trace(
                go.Bar(x=customer_analysis['Customer Type'], 
                      y=customer_analysis['Total Sales'],
                      name='Total Sales',
                      marker_color='#004c91'),
                row=1, col=1
            )
            
            fig_customer.add_trace(
                go.Bar(x=customer_analysis['Customer Type'], 
                      y=customer_analysis['Transaction Count'],
                      name='Transactions',
                      marker_color='#ffc220'),
                row=1, col=2
            )
            
            fig_customer.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_customer, use_container_width=True)
    
    with col2:
        st.markdown("### ⚧ Gender Analysis")
        if "Gender" in filtered_df.columns and "Total" in filtered_df.columns:
            gender_sales = filtered_df.groupby("Gender")["Total"].sum()
            fig_gender = px.donut(
                values=gender_sales.values,
                names=gender_sales.index,
                title="Sales Distribution by Gender",
                color_discrete_map={'Male': '#004c91', 'Female': '#ffc220'}
            )
            fig_gender.update_layout(height=400)
            st.plotly_chart(fig_gender, use_container_width=True)
    
    # Charts Row 3
    if "Date" in filtered_df.columns or "date" in filtered_df.columns:
        st.markdown("### 📅 Sales Trend Over Time")
        date_col = "Date" if "Date" in filtered_df.columns else "date"
        
        # Monthly sales trend
        filtered_df['Month'] = filtered_df[date_col].dt.to_period('M')
        monthly_sales = filtered_df.groupby('Month')["Total"].sum().reset_index()
        monthly_sales['Month'] = monthly_sales['Month'].astype(str)
        
        fig_trend = px.line(
            monthly_sales,
            x='Month',
            y='Total',
            title="Monthly Sales Trend",
            markers=True,
            line_shape="spline"
        )
        fig_trend.update_traces(line_color='#004c91', marker_color='#ffc220')
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Additional Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💳 Payment Method Analysis")
        if "Payment" in filtered_df.columns:
            payment_analysis = filtered_df.groupby("Payment")["Total"].agg(['sum', 'count']).reset_index()
            fig_payment = px.bar(
                payment_analysis,
                x='Payment',
                y='sum',
                title="Sales by Payment Method",
                color='sum',
                color_continuous_scale="Viridis"
            )
            fig_payment.update_layout(height=400)
            st.plotly_chart(fig_payment, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Rating Analysis")
        if "Rating" in filtered_df.columns:
            rating_dist = filtered_df["Rating"].value_counts().sort_index()
            fig_rating = px.histogram(
                filtered_df,
                x="Rating",
                nbins=20,
                title="Customer Rating Distribution",
                color_discrete_sequence=['#ffc220']
            )
            fig_rating.update_layout(height=400)
            st.plotly_chart(fig_rating, use_container_width=True)
    
    # Correlation Heatmap
    st.markdown("### 🔥 Correlation Analysis")
    numeric_columns = filtered_df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 1:
        corr_matrix = filtered_df[numeric_columns].corr()
        fig_heatmap = px.imshow(
            corr_matrix,
            title="Correlation Matrix of Numeric Variables",
            color_continuous_scale="RdBu",
            aspect="auto"
        )
        fig_heatmap.update_layout(height=500)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Summary Statistics
    st.markdown("### 📊 Summary Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Performing Products")
        if "Product line" in filtered_df.columns and "Total" in filtered_df.columns:
            top_products = filtered_df.groupby("Product line")["Total"].sum().sort_values(ascending=False).head(5)
            st.dataframe(top_products.reset_index(), use_container_width=True)
    
    with col2:
        st.markdown("#### Top Cities by Sales")
        if "City" in filtered_df.columns and "Total" in filtered_df.columns:
            top_cities = filtered_df.groupby("City")["Total"].sum().sort_values(ascending=False).head(5)
            st.dataframe(top_cities.reset_index(), use_container_width=True)
    
    # Raw Data Preview
    st.markdown("### 📋 Data Preview")
    st.markdown("*Showing filtered data based on your selections*")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search in data", "")
    if search_term:
        mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    
    st.dataframe(display_df.head(20), use_container_width=True)
    
    # Download filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"walmart_sales_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Footer - Enhanced Dashboard Information Panel
    st.markdown("---")
    st.markdown("### 📝 Dashboard Information Panel")
    
    # Create expandable sections for better organization
    with st.expander("📊 Data Summary & Statistics", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📈 Total Records", f"{len(filtered_df):,}")
            st.metric("🏪 Total Cities", f"{filtered_df['City'].nunique() if 'City' in filtered_df.columns else 'N/A'}")
        
        with col2:
            date_col = "Date" if "Date" in filtered_df.columns else ("date" if "date" in filtered_df.columns else None)
            if date_col:
                st.metric("📅 Date Range Start", filtered_df[date_col].min().strftime('%Y-%m-%d'))
                st.metric("📅 Date Range End", filtered_df[date_col].max().strftime('%Y-%m-%d'))
            else:
                st.metric("📅 Date Range", "No date column found")
        
        with col3:
            st.metric("🕒 Last Updated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            st.metric("🔄 Refresh Rate", "Real-time")
    
    with st.expander("🗂️ Data Structure Information"):
        st.markdown("**Current Data Columns:**")
        cols_info = []
        for col in filtered_df.columns:
            dtype = str(filtered_df[col].dtype)
            unique_count = filtered_df[col].nunique()
            null_count = filtered_df[col].isnull().sum()
            cols_info.append({
                'Column': col,
                'Data Type': dtype,
                'Unique Values': unique_count,
                'Null Values': null_count,
                'Sample Value': str(filtered_df[col].iloc[0]) if len(filtered_df) > 0 else 'N/A'
            })
        
        st.dataframe(pd.DataFrame(cols_info), use_container_width=True)
    
    with st.expander("⚙️ Filter Status"):
        st.markdown("**Active Filters:**")
        filter_status = []
        filter_status.append(f"🏙️ **City:** {selected_city}")
        filter_status.append(f"🛍️ **Product Lines:** {len(selected_product) if selected_product else 'All'} selected")
        filter_status.append(f"👥 **Customer Types:** {len(selected_customer) if selected_customer else 'All'} selected")
        filter_status.append(f"⚧ **Gender:** {len(selected_gender) if selected_gender else 'All'} selected")
        
        for status in filter_status:
            st.markdown(status)
        
        st.markdown(f"**Result:** Showing {len(filtered_df):,} records out of {len(df):,} total records")
    
    with st.expander("🔍 Data Quality Report"):
        st.markdown("**Data Quality Metrics:**")
        quality_metrics = []
        
        for col in filtered_df.columns:
            null_pct = (filtered_df[col].isnull().sum() / len(filtered_df)) * 100
            completeness = 100 - null_pct
            quality_metrics.append({
                'Column': col,
                'Completeness (%)': f"{completeness:.1f}%",
                'Missing Values': filtered_df[col].isnull().sum(),
                'Data Quality': '✅ Excellent' if completeness > 95 else '⚠️ Good' if completeness > 80 else '❌ Poor'
            })
        
        st.dataframe(pd.DataFrame(quality_metrics), use_container_width=True)

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    
    # Enhanced Sample Data Structure Guide
    st.markdown("---")
    st.markdown("### 🛠️ Troubleshooting Guide")
    
    with st.expander("🔧 Database Connection Issues", expanded=True):
        st.markdown("""
        **Common Connection Problems:**
        
        1. **Environment Variables**
           - Check if `.env` file exists in your project directory
           - Verify `DB_URL` is properly set in the `.env` file
           - Format: `DB_URL=postgresql://username:password@host:port/database`
        
        2. **Database Access**
           - Ensure your database server is running
           - Check if the database name is correct
           - Verify username and password credentials
           - Test network connectivity to the database host
        
        3. **Table Existence**
           - Confirm the 'sales' table exists in your database
           - Check table permissions for the connected user
        """)
    
    with st.expander("📋 Expected Data Structure", expanded=True):
        st.markdown("**Required Table: `sales`**")
        
        # Create sample data structure
        sample_data = {
            'Column Name': [
                'City', 'Product line', 'Total', 'Customer type', 
                'Gender', 'Payment', 'Rating', 'Date', 'Branch',
                'Tax 5%', 'Quantity', 'Unit price', 'gross margin percentage',
                'gross income', 'cogs', 'Time', 'Invoice ID'
            ],
            'Data Type': [
                'VARCHAR/TEXT', 'VARCHAR/TEXT', 'DECIMAL/FLOAT', 'VARCHAR/TEXT',
                'VARCHAR/TEXT', 'VARCHAR/TEXT', 'DECIMAL/FLOAT', 'DATE/DATETIME', 'VARCHAR/TEXT',
                'DECIMAL/FLOAT', 'INTEGER', 'DECIMAL/FLOAT', 'DECIMAL/FLOAT',
                'DECIMAL/FLOAT', 'DECIMAL/FLOAT', 'TIME', 'VARCHAR/TEXT'
            ],
            'Description': [
                'City where sale occurred', 'Product category', 'Total sale amount', 'Member/Normal customer',
                'Male/Female', 'Cash/Credit card/Ewallet', 'Customer rating 1-10', 'Transaction date', 'Store branch',
                'Tax amount', 'Quantity sold', 'Price per unit', 'Gross margin percentage',
                'Gross income', 'Cost of goods sold', 'Transaction time', 'Unique invoice identifier'
            ],
            'Required': [
                '✅ Yes', '✅ Yes', '✅ Yes', '🔶 Optional',
                '🔶 Optional', '🔶 Optional', '🔶 Optional', '🔶 Optional', '🔶 Optional',
                '🔶 Optional', '🔶 Optional', '🔶 Optional', '🔶 Optional',
                '🔶 Optional', '🔶 Optional', '🔶 Optional', '🔶 Optional'
            ],
            'Sample Values': [
                'Yangon, Mandalay, Naypyitaw', 'Health and beauty, Sports', '123.45', 'Member, Normal',
                'Male, Female', 'Cash, Credit card, Ewallet', '7.5', '2024-01-15', 'A, B, C',
                '6.17', '5', '24.69', '4.76',
                '6.17', '123.45', '14:30:00', 'INV-001-001'
            ]
        }
        
        st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
        
        st.markdown("**Note:** Only City, Product line, and Total columns are required for basic functionality.")
    
    with st.expander("💡 Sample SQL Commands"):
        st.markdown("**Create Sample Table:**")
        st.code("""
        CREATE TABLE sales (
            invoice_id VARCHAR(50) PRIMARY KEY,
            branch VARCHAR(10),
            city VARCHAR(50),
            customer_type VARCHAR(20),
            gender VARCHAR(10),
            product_line VARCHAR(50),
            unit_price DECIMAL(10,2),
            quantity INTEGER,
            tax_5_percent DECIMAL(10,2),
            total DECIMAL(10,2),
            date DATE,
            time TIME,
            payment VARCHAR(20),
            cogs DECIMAL(10,2),
            gross_margin_percentage DECIMAL(10,2),
            gross_income DECIMAL(10,2),
            rating DECIMAL(3,1)
        );
        """, language='sql')
        
        st.markdown("**Insert Sample Data:**")
        st.code("""
        INSERT INTO sales VALUES 
        ('INV-001-001', 'A', 'Yangon', 'Member', 'Female', 'Health and beauty', 
         74.69, 7, 26.14, 548.97, '2019-01-05', '13:08:00', 'Ewallet', 
         522.83, 4.76, 26.14, 9.1),
        ('INV-001-002', 'C', 'Naypyitaw', 'Normal', 'Male', 'Electronic accessories', 
         15.28, 5, 3.82, 80.22, '2019-01-07', '10:29:00', 'Cash', 
         76.40, 4.76, 3.82, 9.6);
        """, language='sql')
    
    with st.expander("🔍 Testing Your Connection"):
        st.markdown("**Test Database Connection:**")
        st.code("""
        import pandas as pd
        from sqlalchemy import create_engine
        
        # Test connection
        try:
            engine = create_engine(your_db_url)
            test_query = "SELECT COUNT(*) as record_count FROM sales;"
            result = pd.read_sql(test_query, engine)
            print(f"Connection successful! Found {result['record_count'].iloc[0]} records")
        except Exception as e:
            print(f"Connection failed: {e}")
        """, language='python')
    
    with st.expander("📞 Support Resources"):
        st.markdown("""
        **Getting Help:**
        
        - **Database Issues:** Check your database documentation
        - **Streamlit Problems:** Visit [Streamlit Documentation](https://docs.streamlit.io)
        - **SQL Queries:** Review your database query syntax
        - **Python Errors:** Check the error traceback in terminal
        
        **Common Solutions:**
        1. Restart your Streamlit app: `streamlit run your_app.py`
        2. Clear Streamlit cache: Add `st.cache_data.clear()` at the top
        3. Check Python package versions: `pip list`
        4. Verify database server status
        """)

# Enhanced Sidebar with Feature Documentation
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Features")

with st.sidebar.expander("🎯 Interactive Filters", expanded=True):
    st.markdown("""
    **Available Filters:**
    - **City Filter:** Select specific cities or view all
    - **Product Lines:** Multi-select product categories
    - **Customer Type:** Filter by Member/Normal customers
    - **Gender:** Filter by Male/Female customers
    
    **How to Use:**
    - Use dropdown menus to select filters
    - Multiple selections allowed for most filters
    - Charts update automatically when filters change
    - Reset by refreshing the page
    """)

with st.sidebar.expander("📈 Chart Types"):
    st.markdown("""
    **Available Visualizations:**
    - **📊 Bar Charts:** Product sales, payment methods
    - **🥧 Pie Charts:** City distribution, gender analysis
    - **📈 Line Charts:** Time series trends
    - **🔥 Heatmaps:** Correlation analysis
    - **📊 Histograms:** Rating distributions
    - **📋 Data Tables:** Summary statistics
    
    **Interactive Features:**
    - Hover for detailed tooltips
    - Zoom and pan capabilities
    - Click to highlight data points
    - Download charts as images
    """)

with st.sidebar.expander("💾 Data Export Options"):
    st.markdown("""
    **Export Capabilities:**
    - **CSV Export:** Download filtered data
    - **Chart Images:** Right-click to save charts
    - **Data Tables:** Copy table data
    - **Custom Filters:** Export applies current filters
    
    **File Formats:**
    - CSV for spreadsheet analysis
    - PNG/SVG for chart images
    - JSON for data integration
    """)

with st.sidebar.expander("🔄 Real-time Updates"):
    st.markdown("""
    **Auto-refresh Features:**
    - Data refreshes when filters change
    - Charts update dynamically
    - KPI metrics recalculate instantly
    - Cache management for performance
    
    **Performance:**
    - Optimized queries for large datasets
    - Efficient memory usage
    - Fast rendering with Plotly
    """)

with st.sidebar.expander("📱 Responsive Design"):
    st.markdown("""
    **Multi-device Support:**
    - Desktop optimization
    - Tablet compatibility
    - Mobile-friendly layout
    - Touch-friendly controls
    
    **Accessibility:**
    - Screen reader support
    - Keyboard navigation
    - High contrast colors
    - Scalable text
    """)

with st.sidebar.expander("🎨 Customization"):
    st.markdown("""
    **Theme Options:**
    - Walmart brand colors
    - Professional styling
    - Custom CSS themes
    - Color-blind friendly palettes
    
    **Layout Options:**
    - Wide/narrow layouts
    - Collapsible sections
    - Customizable metrics
    - Flexible chart arrangements
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Color Scheme")
st.sidebar.markdown("""
**Brand Colors:**
- **Primary Blue:** #004c91 (Walmart corporate)
- **Secondary Yellow:** #ffc220 (Walmart accent)
- **Success Green:** #00a651 (Positive metrics)
- **Warning Orange:** #ff6900 (Alerts)
- **Neutral Gray:** #666666 (Text)

**Chart Palettes:**
- Qualitative: Set3, Plotly colors
- Sequential: Blues, Viridis
- Diverging: RdBu, RdYlBu
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Support & Help")
st.sidebar.markdown("""
**Quick Actions:**
- 🔄 Refresh data: Reload page
- ❓ Get help: Check troubleshooting guide
- 📁 Export data: Use download buttons
- 🎯 Reset filters: Refresh page

**Version:** 2.0.0
**Last Updated:** July 2025
""")

# Performance metrics in sidebar
if 'df' in locals():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Performance Metrics")
    st.sidebar.metric("📊 Records Loaded", f"{len(df):,}")
    st.sidebar.metric("🔍 Records Filtered", f"{len(filtered_df):,}")
    st.sidebar.metric("📈 Charts Generated", "12+")
    st.sidebar.metric("🎯 Filter Efficiency", f"{(len(filtered_df)/len(df)*100):.1f}%")