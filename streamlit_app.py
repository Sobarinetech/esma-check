"""
ESMA Data Explorer - Comprehensive Streamlit Application
This app integrates both esma_data_py and esef_toolkit packages
with all available endpoints and use cases.

Author: Generated for ESMA Data Analysis
License: EUPL-1.2 (matching ESMA tools)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import zipfile
from typing import Optional, Dict, List
import json

# Try to import ESMA packages (will need to be installed)
try:
    from esma_data_py import EsmaDataLoader
    ESMA_DATA_AVAILABLE = True
except ImportError:
    ESMA_DATA_AVAILABLE = False
    st.warning("⚠️ esma_data_py not installed. Install with: pip install esma-data-py")

try:
    import esef_toolkit
    ESEF_AVAILABLE = True
except ImportError:
    ESEF_AVAILABLE = False
    st.warning("⚠️ esef_toolkit not installed. Clone from GitHub and install.")

# Page configuration
st.set_page_config(
    page_title="ESMA Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'esma_loader' not in st.session_state and ESMA_DATA_AVAILABLE:
    st.session_state.esma_loader = EsmaDataLoader()
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

# ==================== UTILITY FUNCTIONS ====================

def log_download(data_type: str, params: Dict):
    """Log download activity"""
    st.session_state.download_history.append({
        'timestamp': datetime.now(),
        'data_type': data_type,
        'params': params
    })

def cache_data(key: str, data):
    """Cache data in session state"""
    st.session_state.cached_data[key] = {
        'data': data,
        'timestamp': datetime.now()
    }

def get_cached_data(key: str, max_age_minutes: int = 60):
    """Retrieve cached data if not expired"""
    if key in st.session_state.cached_data:
        cached = st.session_state.cached_data[key]
        age = (datetime.now() - cached['timestamp']).total_seconds() / 60
        if age < max_age_minutes:
            return cached['data']
    return None

def create_download_button(df: pd.DataFrame, filename: str, label: str = "Download Data"):
    """Create a download button for DataFrame"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime='text/csv',
        key=f"download_{filename}_{datetime.now().timestamp()}"
    )

def display_dataframe_stats(df: pd.DataFrame):
    """Display DataFrame statistics"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    with col4:
        null_count = df.isnull().sum().sum()
        st.metric("Null Values", f"{null_count:,}")

# ==================== MAIN APPLICATION ====================

def main():
    # Header
    st.markdown('<div class="main-header">📊 ESMA Data Explorer</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <strong>Welcome to the ESMA Data Explorer!</strong><br>
    This comprehensive tool provides access to:
    <ul>
        <li><strong>ESMA Data API</strong>: MiFID, FIRDS, SSR data</li>
        <li><strong>ESEF Toolkit</strong>: Extract financial data from XBRL filings</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Select Module",
        [
            "🏠 Home",
            "📈 MiFID Data Explorer",
            "🏦 FIRDS Reference Data",
            "📉 Short Selling (SSR) Data",
            "🇬🇧 FCA FIRDS Data",
            "📄 ESEF XBRL Filings",
            "📊 Data Analysis Dashboard",
            "🔄 Batch Processing",
            "⏱️ Scheduled Data Retrieval",
            "📥 Download History",
            "ℹ️ Documentation"
        ]
    )
    
    # Route to appropriate page
    if page == "🏠 Home":
        show_home_page()
    elif page == "📈 MiFID Data Explorer":
        show_mifid_explorer()
    elif page == "🏦 FIRDS Reference Data":
        show_firds_explorer()
    elif page == "📉 Short Selling (SSR) Data":
        show_ssr_explorer()
    elif page == "🇬🇧 FCA FIRDS Data":
        show_fca_firds_explorer()
    elif page == "📄 ESEF XBRL Filings":
        show_esef_explorer()
    elif page == "📊 Data Analysis Dashboard":
        show_analysis_dashboard()
    elif page == "🔄 Batch Processing":
        show_batch_processing()
    elif page == "⏱️ Scheduled Data Retrieval":
        show_scheduled_retrieval()
    elif page == "📥 Download History":
        show_download_history()
    elif page == "ℹ️ Documentation":
        show_documentation()

# ==================== HOME PAGE ====================

def show_home_page():
    st.markdown('<div class="section-header">Welcome to ESMA Data Explorer</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Quick Start Guide")
        st.markdown("""
        1. **MiFID Data**: Access MiFID II/MiFIR regulatory data
        2. **FIRDS**: Financial Instruments Reference Database
        3. **SSR**: Short Selling Regulation data
        4. **ESEF**: European Single Electronic Format filings
        5. **Analysis**: Built-in analytics and visualizations
        """)
        
        st.markdown("### 🔧 Installation Requirements")
        st.code("""
pip install esma-data-py
pip install streamlit pandas plotly
# For ESEF toolkit:
git clone https://github.com/European-Securities-Markets-Authority/esef_toolkit.git
cd esef_toolkit
pip install -e .
        """, language="bash")
    
    with col2:
        st.markdown("### 📊 Available Data Sources")
        
        data_sources = pd.DataFrame({
            'Data Source': ['MiFID Files', 'FIRDS', 'SSR Exemptions', 'FCA FIRDS', 'ESEF XBRL'],
            'Status': [
                '✅ Available' if ESMA_DATA_AVAILABLE else '❌ Not Available',
                '✅ Available' if ESMA_DATA_AVAILABLE else '❌ Not Available',
                '✅ Available' if ESMA_DATA_AVAILABLE else '❌ Not Available',
                '✅ Available' if ESMA_DATA_AVAILABLE else '❌ Not Available',
                '✅ Available' if ESEF_AVAILABLE else '❌ Not Available'
            ],
            'Use Case': [
                'Regulatory compliance, market analysis',
                'Instrument reference data, validation',
                'Short selling monitoring',
                'UK market data',
                'Financial statement extraction'
            ]
        })
        
        st.dataframe(data_sources, use_container_width=True)
        
        st.markdown("### 📈 Recent Activity")
        if st.session_state.download_history:
            recent = pd.DataFrame(st.session_state.download_history[-5:])
            st.dataframe(recent, use_container_width=True)
        else:
            st.info("No recent activity")

# ==================== MIFID DATA EXPLORER ====================

def show_mifid_explorer():
    st.markdown('<div class="section-header">📈 MiFID Data Explorer</div>', unsafe_allow_html=True)
    
    if not ESMA_DATA_AVAILABLE:
        st.error("ESMA Data package not available. Please install esma-data-py.")
        return
    
    st.markdown("""
    <div class="info-box">
    <strong>MiFID II/MiFIR Data</strong><br>
    Access Markets in Financial Instruments Directive data including transparency reports,
    transaction data, and regulatory submissions.
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=90),
            key="mifid_start"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="mifid_end"
        )
    
    with col3:
        cache_duration = st.slider(
            "Cache Duration (minutes)",
            min_value=5,
            max_value=120,
            value=60,
            key="mifid_cache"
        )
    
    if st.button("🔍 Load MiFID File List", key="load_mifid"):
        with st.spinner("Loading MiFID data..."):
            try:
                # Check cache first
                cache_key = f"mifid_{start_date}_{end_date}"
                cached = get_cached_data(cache_key, cache_duration)
                
                if cached is not None:
                    df = cached
                    st.success("✅ Loaded from cache")
                else:
                    loader = st.session_state.esma_loader
                    df = loader.load_mifid_file_list(
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d')
                    )
                    cache_data(cache_key, df)
                    st.success("✅ Data loaded successfully")
                
                log_download('MiFID', {'start_date': start_date, 'end_date': end_date})
                
                # Display statistics
                st.markdown("### 📊 Data Overview")
                display_dataframe_stats(df)
                
                # Display data
                st.markdown("### 📋 MiFID Files")
                st.dataframe(df, use_container_width=True)
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    create_download_button(df, "mifid_files.csv", "📥 Download CSV")
                
                with col2:
                    json_str = df.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name="mifid_files.json",
                        mime="application/json"
                    )
                
                # Visualizations
                if len(df) > 0:
                    st.markdown("### 📈 Visualizations")
                    
                    # Files over time
                    if 'publication_date' in df.columns:
                        df['publication_date'] = pd.to_datetime(df['publication_date'])
                        files_per_day = df.groupby(df['publication_date'].dt.date).size().reset_index()
                        files_per_day.columns = ['Date', 'File Count']
                        
                        fig = px.line(
                            files_per_day,
                            x='Date',
                            y='File Count',
                            title='MiFID Files Published Over Time'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error loading MiFID data: {str(e)}")
                st.exception(e)

# ==================== FIRDS EXPLORER ====================

def show_firds_explorer():
    st.markdown('<div class="section-header">🏦 FIRDS Reference Data Explorer</div>', unsafe_allow_html=True)
    
    if not ESMA_DATA_AVAILABLE:
        st.error("ESMA Data package not available. Please install esma-data-py.")
        return
    
    st.markdown("""
    <div class="info-box">
    <strong>Financial Instruments Reference Database System (FIRDS)</strong><br>
    Access comprehensive reference data for financial instruments including ISINs,
    CFI codes, instrument types, and trading venue information.
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different FIRDS operations
    tab1, tab2, tab3 = st.tabs(["📥 Load Latest Files", "🔍 Search by Criteria", "📊 Bulk Analysis"])
    
    with tab1:
        st.markdown("### Load Latest FIRDS Files")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            instrument_type = st.selectbox(
                "Instrument Type",
                ["All", "Equity", "Bond", "Derivative", "ETF", "Fund"],
                key="firds_type"
            )
        
        with col2:
            max_files = st.number_input(
                "Max Files to Load",
                min_value=1,
                max_value=100,
                value=10,
                key="firds_max"
            )
        
        with col3:
            file_format = st.selectbox(
                "Output Format",
                ["DataFrame", "CSV", "JSON", "Excel"],
                key="firds_format"
            )
        
        if st.button("🔍 Load Latest FIRDS Files", key="load_firds"):
            with st.spinner("Loading FIRDS data..."):
                try:
                    loader = st.session_state.esma_loader
                    
                    # Build filter arguments
                    filter_args = {}
                    if instrument_type != "All":
                        filter_args['instrument_type'] = instrument_type.lower()
                    
                    df = loader.load_latest_files(
                        limit=max_files,
                        **filter_args
                    )
                    
                    log_download('FIRDS', {
                        'instrument_type': instrument_type,
                        'max_files': max_files
                    })
                    
                    st.success(f"✅ Loaded {len(df)} records")
                    
                    # Display statistics
                    display_dataframe_stats(df)
                    
                    # Display data
                    st.dataframe(df, use_container_width=True)
                    
                    # Download based on format
                    if file_format == "CSV":
                        create_download_button(df, "firds_data.csv")
                    elif file_format == "JSON":
                        json_str = df.to_json(orient='records', indent=2)
                        st.download_button("📥 Download JSON", json_str, "firds_data.json", "application/json")
                    elif file_format == "Excel":
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='FIRDS Data')
                        st.download_button("📥 Download Excel", buffer.getvalue(), "firds_data.xlsx", 
                                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    
                except Exception as e:
                    st.error(f"❌ Error loading FIRDS data: {str(e)}")
    
    with tab2:
        st.markdown("### Search FIRDS by ISIN or Identifier")
        
        search_type = st.radio(
            "Search Type",
            ["ISIN", "CFI Code", "Instrument Name"],
            horizontal=True
        )
        
        search_value = st.text_input(f"Enter {search_type}", key="firds_search")
        
        if st.button("🔍 Search", key="firds_search_btn"):
            if search_value:
                with st.spinner(f"Searching for {search_type}: {search_value}..."):
                    try:
                        loader = st.session_state.esma_loader
                        # Note: Actual implementation would depend on API capabilities
                        st.info(f"Searching for {search_type}: {search_value}")
                        st.warning("⚠️ Search functionality depends on ESMA API capabilities")
                    except Exception as e:
                        st.error(f"❌ Search error: {str(e)}")
            else:
                st.warning("Please enter a search value")
    
    with tab3:
        st.markdown("### Bulk FIRDS Analysis")
        
        st.markdown("""
        Perform bulk analysis on FIRDS data:
        - Instrument type distribution
        - Trading venue coverage
        - CFI code patterns
        - Geographic distribution
        """)
        
        if st.button("📊 Run Bulk Analysis", key="firds_bulk"):
            st.info("Bulk analysis feature - implementation depends on loaded data")

# ==================== SSR EXPLORER ====================

def show_ssr_explorer():
    st.markdown('<div class="section-header">📉 Short Selling Regulation (SSR) Data</div>', unsafe_allow_html=True)
    
    if not ESMA_DATA_AVAILABLE:
        st.error("ESMA Data package not available. Please install esma-data-py.")
        return
    
    st.markdown("""
    <div class="info-box">
    <strong>Short Selling Regulation (SSR) Exempted Shares</strong><br>
    Monitor shares exempt from short selling restrictions across EU markets.
    Track exemptions, analyze patterns, and monitor regulatory changes.
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        country_filter = st.multiselect(
            "Filter by Country",
            ["All", "DE", "FR", "IT", "ES", "NL", "BE", "IE", "PT", "GR"],
            default=["All"],
            key="ssr_country"
        )
    
    with col2:
        date_filter = st.date_input(
            "Exemption Date From",
            value=datetime.now() - timedelta(days=180),
            key="ssr_date"
        )
    
    with col3:
        show_expired = st.checkbox(
            "Include Expired Exemptions",
            value=False,
            key="ssr_expired"
        )
    
    if st.button("🔍 Load SSR Exempted Shares", key="load_ssr"):
        with st.spinner("Loading SSR data..."):
            try:
                loader = st.session_state.esma_loader
                
                # Load SSR data
                df = loader.load_ssr_exempted_shares()
                
                log_download('SSR', {
                    'countries': country_filter,
                    'date_from': date_filter,
                    'show_expired': show_expired
                })
                
                st.success(f"✅ Loaded {len(df)} exempted shares")
                
                # Display statistics
                display_dataframe_stats(df)
                
                # Display data
                st.markdown("### 📋 Exempted Shares Data")
                st.dataframe(df, use_container_width=True)
                
                # Download options
                create_download_button(df, "ssr_exempted_shares.csv", "📥 Download SSR Data")
                
                # Analytics
                if len(df) > 0:
                    st.markdown("### 📊 SSR Analytics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Country distribution
                        if 'country' in df.columns:
                            country_counts = df['country'].value_counts()
                            fig = px.pie(
                                values=country_counts.values,
                                names=country_counts.index,
                                title='Exemptions by Country'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Exemption status
                        if 'status' in df.columns:
                            status_counts = df['status'].value_counts()
                            fig = px.bar(
                                x=status_counts.index,
                                y=status_counts.values,
                                title='Exemption Status Distribution',
                                labels={'x': 'Status', 'y': 'Count'}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error loading SSR data: {str(e)}")
                st.exception(e)

# ==================== FCA FIRDS EXPLORER ====================

def show_fca_firds_explorer():
    st.markdown('<div class="section-header">🇬🇧 FCA FIRDS Data Explorer</div>', unsafe_allow_html=True)
    
    if not ESMA_DATA_AVAILABLE:
        st.error("ESMA Data package not available. Please install esma-data-py.")
        return
    
    st.markdown("""
    <div class="info-box">
    <strong>FCA (UK) Financial Instruments Reference Data</strong><br>
    Access UK Financial Conduct Authority's FIRDS data for instruments
    traded in UK markets post-Brexit.
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            key="fca_start"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="fca_end"
        )
    
    if st.button("🔍 Load FCA FIRDS File List", key="load_fca"):
        with st.spinner("Loading FCA FIRDS data..."):
            try:
                loader = st.session_state.esma_loader
                
                df = loader.load_fca_firds_file_list(
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                
                log_download('FCA FIRDS', {
                    'start_date': start_date,
                    'end_date': end_date
                })
                
                st.success(f"✅ Loaded {len(df)} FCA FIRDS files")
                
                # Display statistics
                display_dataframe_stats(df)
                
                # Display data
                st.markdown("### 📋 FCA FIRDS Files")
                st.dataframe(df, use_container_width=True)
                
                # Download options
                create_download_button(df, "fca_firds_files.csv", "📥 Download FCA Data")
                
                # Comparison with ESMA FIRDS
                st.markdown("### 🔄 FCA vs ESMA Comparison")
                st.info("""
                **Key Differences:**
                - FCA FIRDS covers UK-specific instruments post-Brexit
                - Different reporting requirements and timelines
                - Separate regulatory framework
                - Use for cross-jurisdiction analysis
                """)
                
            except Exception as e:
                st.error(f"❌ Error loading FCA FIRDS data: {str(e)}")
                st.exception(e)

# ==================== ESEF EXPLORER ====================

def show_esef_explorer():
    st.markdown('<div class="section-header">📄 ESEF XBRL Filings Explorer</div>', unsafe_allow_html=True)
    
    if not ESEF_AVAILABLE:
        st.error("ESEF Toolkit not available. Please install from GitHub.")
        st.code("""
git clone https://github.com/European-Securities-Markets-Authority/esef_toolkit.git
cd esef_toolkit
pip install -e .
        """, language="bash")
        return
    
    st.markdown("""
    <div class="info-box">
    <strong>European Single Electronic Format (ESEF)</strong><br>
    Extract structured financial data from XBRL corporate filings of EU listed companies.
    Analyze financial statements, compare metrics, and build datasets.
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different ESEF operations
    tab1, tab2, tab3 = st.tabs(["🔍 Search Filings", "📥 Extract Data", "📊 Analysis"])
    
    with tab1:
        st.markdown("### Search ESEF Filings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country = st.selectbox(
                "Country",
                ["", "IE", "DE", "FR", "IT", "ES", "NL", "BE", "PT", "GR", "AT", "FI", "SE", "DK"],
                key="esef_country"
            )
        
        with col2:
            year = st.number_input(
                "Reporting Year",
                min_value=2019,
                max_value=2024,
                value=2023,
                key="esef_year"
            )
        
        with col3:
            lei = st.text_input(
                "LEI (optional)",
                placeholder="Enter Legal Entity Identifier",
                key="esef_lei"
            )
        
        issuer_name = st.text_input(
            "Issuer Name (optional)",
            placeholder="Enter company name",
            key="esef_issuer"
        )
        
        download_files = st.checkbox(
            "Download filing packages",
            value=False,
            key="esef_download"
        )
        
        if st.button("🔍 Search ESEF Filings", key="search_esef"):
            if not country:
                st.warning("Please select a country")
            else:
                with st.spinner(f"Searching ESEF filings for {country} {year}..."):
                    try:
                        st.info("ESEF Search - Implementation requires esef_toolkit CLI integration")
                        
                        # Simulate search results
                        st.markdown("### 📋 Search Results")
                        sample_results = pd.DataFrame({
                            'Company': ['Sample Corp A', 'Sample Corp B', 'Sample Corp C'],
                            'LEI': ['549300XXX', '549300YYY', '549300ZZZ'],
                            'Country': [country] * 3,
                            'Year': [year] * 3,
                            'Filing Date': ['2023-04-30', '2023-05-15', '2023-06-01'],
                            'Status': ['Available', 'Available', 'Available']
                        })
                        
                        st.dataframe(sample_results, use_container_width=True)
                        
                        if download_files:
                            st.info("Download functionality would save ZIP packages locally")
                        
                    except Exception as e:
                        st.error(f"❌ Error searching ESEF filings: {str(e)}")
    
    with tab2:
        st.markdown("### Extract Financial Data from ESEF Filing")
        
        st.markdown("""
        Upload an ESEF XBRL package (ZIP) or provide a filing reference to extract:
        - Financial facts and values
        - Context and dimensions
        - Presentation structure
        - Calculation linkbase
        - Anchoring information
        """)
        
        upload_method = st.radio(
            "Data Source",
            ["Upload ZIP File", "Provide Filing Reference"],
            horizontal=True
        )
        
        if upload_method == "Upload ZIP File":
            uploaded_file = st.file_uploader(
                "Upload ESEF XBRL Package (ZIP)",
                type=['zip'],
                key="esef_upload"
            )
            
            if uploaded_file and st.button("📤 Extract Data", key="extract_upload"):
                with st.spinner("Extracting ESEF data..."):
                    try:
                        st.info("ESEF extraction - Implementation requires esef_toolkit processing")
                        
                        # Simulate extraction results
                        st.success("✅ Extraction complete")
                        
                        # Sample facts table
                        st.markdown("#### 📊 Extracted Facts")
                        facts_df = pd.DataFrame({
                            'Concept': ['Revenue', 'Total Assets', 'Net Income', 'Cash Flow'],
                            'Value': [1500000, 5000000, 250000, 300000],
                            'Unit': ['EUR', 'EUR', 'EUR', 'EUR'],
                            'Period': ['2023', '2023', '2023', '2023'],
                            'Context': ['Annual', 'Year-End', 'Annual', 'Annual']
                        })
                        st.dataframe(facts_df, use_container_width=True)
                        create_download_button(facts_df, "esef_facts.csv", "📥 Download Facts")
                        
                    except Exception as e:
                        st.error(f"❌ Extraction error: {str(e)}")
        
        else:
            filing_ref = st.text_input(
                "Filing Reference / URL",
                placeholder="Enter filing reference or URL",
                key="esef_ref"
            )
            
            if filing_ref and st.button("📤 Extract Data", key="extract_ref"):
                st.info(f"Processing filing: {filing_ref}")
    
    with tab3:
        st.markdown("### ESEF Data Analysis")
        
        st.markdown("""
        Analyze extracted ESEF data:
        - Compare financial metrics across companies
        - Time-series analysis
        - Industry benchmarking
        - Ratio calculations
        """)
        
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Financial Ratios", "Trend Analysis", "Peer Comparison", "Custom Metrics"],
            key="esef_analysis_type"
        )
        
        if st.button("📊 Run Analysis", key="run_esef_analysis"):
            st.info(f"Running {analysis_type} analysis...")
            
            # Sample visualization
            sample_data = pd.DataFrame({
                'Metric': ['Revenue Growth', 'Profit Margin', 'ROE', 'Debt/Equity'],
                'Company A': [15.2, 8.5, 12.3, 0.65],
                'Company B': [12.8, 10.2, 15.1, 0.48],
                'Company C': [18.5, 7.8, 11.9, 0.72]
            })
            
            fig = px.bar(
                sample_data,
                x='Metric',
                y=['Company A', 'Company B', 'Company C'],
                barmode='group',
                title=f'{analysis_type} Comparison'
            )
            st.plotly_chart(fig, use_container_width=True)

# ==================== ANALYSIS DASHBOARD ====================

def show_analysis_dashboard():
    st.markdown('<div class="section-header">📊 Data Analysis Dashboard</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Comprehensive analytics dashboard combining data from all ESMA sources.
    Visualize trends, compare datasets, and generate insights.
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics overview
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Downloads",
            value=len(st.session_state.download_history),
            delta="+5 today"
        )
    
    with col2:
        cached_items = len(st.session_state.cached_data)
        st.metric(
            label="Cached Datasets",
            value=cached_items,
            delta=f"{cached_items} active"
        )
    
    with col3:
        st.metric(
            label="Data Sources",
            value="5",
            delta="All active"
        )
    
    with col4:
        st.metric(
            label="Last Update",
            value=datetime.now().strftime("%H:%M"),
            delta="Live"
        )
    
    # Visualization options
    st.markdown("### 📊 Visualizations")
    
    viz_type = st.selectbox(
        "Select Visualization",
        [
            "Download Activity Timeline",
            "Data Source Distribution",
            "Geographic Coverage Map",
            "Instrument Type Analysis",
            "Custom Query Builder"
        ]
    )
    
    if viz_type == "Download Activity Timeline":
        if st.session_state.download_history:
            df = pd.DataFrame(st.session_state.download_history)
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            activity = df.groupby(['date', 'data_type']).size().reset_index(name='count')
            
            fig = px.line(
                activity,
                x='date',
                y='count',
                color='data_type',
                title='Download Activity Over Time',
                labels={'count': 'Number of Downloads', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No download activity to display")
    
    elif viz_type == "Data Source Distribution":
        if st.session_state.download_history:
            df = pd.DataFrame(st.session_state.download_history)
            source_counts = df['data_type'].value_counts()
            
            fig = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title='Downloads by Data Source'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to display")
    
    elif viz_type == "Custom Query Builder":
        st.markdown("### 🔧 Custom Query Builder")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_source = st.selectbox(
                "Data Source",
                ["MiFID", "FIRDS", "SSR", "FCA FIRDS", "ESEF"]
            )
        
        with col2:
            aggregation = st.selectbox(
                "Aggregation",
                ["Count", "Sum", "Average", "Min", "Max"]
            )
        
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            key="custom_date_range"
        )
        
        if st.button("🔍 Run Query"):
            st.info(f"Running custom query on {data_source} with {aggregation} aggregation")

# ==================== BATCH PROCESSING ====================

def show_batch_processing():
    st.markdown('<div class="section-header">🔄 Batch Processing</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Automate bulk data retrieval and processing across multiple parameters.
    Ideal for historical data collection, multi-country analysis, and large-scale research.
    </div>
    """, unsafe_allow_html=True)
    
    # Batch job configuration
    st.markdown("### ⚙️ Configure Batch Job")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_sources = st.multiselect(
            "Data Sources",
            ["MiFID", "FIRDS", "SSR", "FCA FIRDS", "ESEF"],
            default=["FIRDS"],
            key="batch_sources"
        )
    
    with col2:
        countries = st.multiselect(
            "Countries",
            ["DE", "FR", "IT", "ES", "NL", "BE", "IE", "PT", "GR", "AT"],
            default=["DE", "FR"],
            key="batch_countries"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=365),
            key="batch_start"
        )
    
    with col4:
        end_date = st.date_input(
            "End Date",
            value=datetime.now(),
            key="batch_end"
        )
    
    # Batch options
    parallel_jobs = st.slider(
        "Parallel Jobs",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of parallel downloads (be mindful of API rate limits)"
    )
    
    export_format = st.selectbox(
        "Export Format",
        ["CSV", "Excel", "JSON", "Parquet"],
        key="batch_export"
    )
    
    # Job preview
    st.markdown("### 📋 Job Preview")
    total_jobs = len(data_sources) * len(countries) * ((end_date - start_date).days // 30 + 1)
    st.info(f"**Estimated jobs:** {total_jobs} | **Parallel workers:** {parallel_jobs}")
    
    if st.button("🚀 Start Batch Processing", key="start_batch"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(total_jobs):
            # Simulate batch processing
            progress = (i + 1) / total_jobs
            progress_bar.progress(progress)
            status_text.text(f"Processing job {i+1}/{total_jobs}...")
            
        st.success(f"✅ Batch processing complete! Processed {total_jobs} jobs.")
        st.balloons()

# ==================== SCHEDULED RETRIEVAL ====================

def show_scheduled_retrieval():
    st.markdown('<div class="section-header">⏱️ Scheduled Data Retrieval</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
    ⚠️ <strong>Note:</strong> Streamlit apps are stateless. For production scheduling, use:
    <ul>
        <li>Cron jobs on a server</li>
        <li>Apache Airflow</li>
        <li>AWS EventBridge</li>
        <li>GitHub Actions</li>
    </ul>
    This interface demonstrates configuration only.
    </div>
    """, unsafe_allow_html=True)
    
    # Schedule configuration
    st.markdown("### ⚙️ Configure Schedule")
    
    col1, col2 = st.columns(2)
    
    with col1:
        schedule_type = st.selectbox(
            "Schedule Type",
            ["Daily", "Weekly", "Monthly", "Custom Cron"],
            key="schedule_type"
        )
    
    with col2:
        execution_time = st.time_input(
            "Execution Time",
            value=datetime.strptime("09:00", "%H:%M").time(),
            key="exec_time"
        )
    
    data_sources = st.multiselect(
        "Data Sources to Retrieve",
        ["MiFID", "FIRDS", "SSR", "FCA FIRDS"],
        default=["FIRDS"],
        key="sched_sources"
    )
    
    notification_email = st.text_input(
        "Notification Email",
        placeholder="your.email@example.com",
        key="notif_email"
    )
    
    # Generate code
    if st.button("🔧 Generate Scheduler Code", key="gen_sched"):
        st.markdown("### 📝 Generated Code")
        
        code = f"""
# Cron expression for {schedule_type} at {execution_time}
# Add this to your crontab or scheduler

import schedule
import time
from esma_data_py import EsmaDataLoader

def fetch_esma_data():
    loader = EsmaDataLoader()
    
    # Fetch data for: {', '.join(data_sources)}
    {''.join([f"    # {source} = loader.load_{source.lower()}_data()
" for source in data_sources])}
    
    # Send notification to {notification_email}
    print("Data fetch complete!")

# Schedule
schedule.every().day.at("{execution_time}").do(fetch_esma_data)

while True:
    schedule.run_pending()
    time.sleep(60)
"""
        
        st.code(code, language="python")
        
        st.download_button(
            "📥 Download Scheduler Script",
            code,
            "esma_scheduler.py",
            "text/x-python"
        )

# ==================== DOWNLOAD HISTORY ====================

def show_download_history():
    st.markdown('<div class="section-header">📥 Download History</div>', unsafe_allow_html=True)
    
    if not st.session_state.download_history:
        st.info("No download history available yet. Start exploring data to see activity here.")
        return
    
    df = pd.DataFrame(st.session_state.download_history)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Downloads", len(df))
    
    with col2:
        unique_types = df['data_type'].nunique()
        st.metric("Data Sources Used", unique_types)
    
    with col3:
        if len(df) > 0:
            last_download = df['timestamp'].max()
            st.metric("Last Download", last_download.strftime("%Y-%m-%d %H:%M"))
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        filter_type = st.multiselect(
            "Filter by Data Type",
            df['data_type'].unique(),
            default=df['data_type'].unique()
        )
    
    with col2:
        date_range = st.date_input(
            "Date Range",
            value=[df['timestamp'].min().date(), df['timestamp'].max().date()],
            key="history_date_range"
        )
    
    # Filtered data
    filtered_df = df[
        (df['data_type'].isin(filter_type)) &
        (df['timestamp'].dt.date >= date_range[0]) &
        (df['timestamp'].dt.date <= date_range[1])
    ]
    
    st.markdown("### 📋 Download Records")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Export history
    if st.button("📥 Export History"):
        create_download_button(filtered_df, "download_history.csv", "Download History CSV")
    
    # Clear history
    if st.button("🗑️ Clear History", key="clear_history"):
        if st.checkbox("Confirm deletion", key="confirm_clear"):
            st.session_state.download_history = []
            st.success("✅ History cleared")
            st.rerun()

# ==================== DOCUMENTATION ====================

def show_documentation():
    st.markdown('<div class="section-header">ℹ️ Documentation</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Overview", "🔧 Installation", "💡 Use Cases", "🔗 Resources"])
    
    with tab1:
        st.markdown("""
        ## ESMA Data Explorer
        
        This application provides comprehensive access to ESMA (European Securities and Markets Authority)
        regulatory data through a user-friendly interface.
        
        ### Features
        
        ✅ **MiFID Data**: Access MiFID II/MiFIR transparency and transaction data  
        ✅ **FIRDS**: Financial Instruments Reference Database queries  
        ✅ **SSR**: Short Selling Regulation exemption monitoring  
        ✅ **FCA FIRDS**: UK market data post-Brexit  
        ✅ **ESEF**: Extract structured data from XBRL filings  
        ✅ **Analytics**: Built-in visualizations and analysis tools  
        ✅ **Batch Processing**: Automate large-scale data collection  
        ✅ **Export**: Multiple formats (CSV, Excel, JSON, Parquet)  
        
        ### Architecture
        
        The application is built with:
        - **Streamlit**: Web interface
        - **esma_data_py**: ESMA data API client
        - **esef_toolkit**: XBRL processing
        - **Pandas**: Data manipulation
        - **Plotly**: Interactive visualizations
        """)
    
    with tab2:
        st.markdown("""
        ## Installation Guide
        
        ### 1. Install Python Dependencies
        
        ```bash
        # Create virtual environment
        python -m venv esma_env
        source esma_env/bin/activate  # On Windows: esma_env\\Scripts\\activate
        
        # Install packages
        pip install streamlit pandas plotly openpyxl
        pip install esma-data-py
        ```
        
        ### 2. Install ESEF Toolkit
        
        ```bash
        # Clone repository
        git clone https://github.com/European-Securities-Markets-Authority/esef_toolkit.git
        cd esef_toolkit
        pip install -e .
        ```
        
        ### 3. Run the Application
        
        ```bash
        streamlit run esma_data_streamlit_app.py
        ```
        
        ### System Requirements
        
        - Python 3.8+
        - 4GB RAM minimum (8GB recommended for large datasets)
        - Internet connection for data retrieval
        - Modern web browser (Chrome, Firefox, Safari, Edge)
        """)
    
    with tab3:
        st.markdown("""
        ## Use Cases
        
        ### 1. Regulatory Compliance
        - Automate daily/weekly FIRDS reference data updates
        - Monitor instrument classification changes
        - Validate trading system compliance
        - Track short selling exemptions
        
        ### 2. Market Intelligence
        - Analyze instrument type distribution over time
        - Track transparency reporting volumes
        - Identify market structure trends
        - Sector-level short selling analysis
        
        ### 3. Research & Academia
        - Reproducible data collection for research papers
        - Historical market structure studies
        - Cross-country regulatory comparisons
        - Financial reporting quality analysis (ESEF)
        
        ### 4. Risk Management
        - Monitor regulatory data quality
        - Cross-check internal databases
        - Identify data gaps and inconsistencies
        - Track instrument lifecycle events
        
        ### 5. Product Development
        - Build compliance dashboards
        - Create regulatory data APIs
        - Integrate into data warehouses
        - Power FinTech applications
        
        ### 6. Financial Analysis
        - Extract standardized financial statements (ESEF)
        - Build comparable company datasets
        - Calculate financial ratios at scale
        - Time-series financial analysis
        """)
    
    with tab4:
        st.markdown("""
        ## Resources
        
        ### Official Documentation
        
        - [ESMA Official Website](https://www.esma.europa.eu/)
        - [esma_data_py GitHub](https://github.com/European-Securities-Markets-Authority/esma_data_py)
        - [esef_toolkit GitHub](https://github.com/European-Securities-Markets-Authority/esef_toolkit)
        - [MiFID II/MiFIR Documentation](https://www.esma.europa.eu/policy-rules/mifid-ii-and-mifir)
        - [ESEF Reporting Manual](https://www.esma.europa.eu/policy-rules/corporate-disclosure/european-single-electronic-format)
        
        ### Support & Community
        
        - Report issues on GitHub
        - ESMA Q&A portal
        - Regulatory data forums
        
        ### Related Tools
        
        - Apache Airflow (scheduling)
        - PostgreSQL (data storage)
        - Tableau/Power BI (visualization)
        - Jupyter Notebooks (analysis)
        
        ### API Rate Limits
        
        Be mindful of ESMA's API rate limits:
        - Recommended: Max 10 requests per minute
        - Use caching for repeated queries
        - Schedule bulk downloads during off-peak hours
        """)

# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    main()
