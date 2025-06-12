import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import numpy as np
from datetime import datetime
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Netflix dark theme
st.markdown("""
    <style>
    /* Global styles */
    .stApp {
        background-color: #141414;
        color: #ffffff;
    }
    
    /* Main container styling */
    .main {
        padding: 2rem;
        background-color: #141414;
    }
    
    /* Header styling */
    .header {
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #333333;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #333333;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #1f1f1f;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 10px;
        padding-bottom: 10px;
        transition: all 0.3s ease;
        color: #808080;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1f1f1f;
        border-bottom: 2px solid #E50914;
        color: #ffffff;
    }
    
    /* Metric card styling */
    .metric-card {
        background-color: #1f1f1f;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #333333;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
        border-color: #E50914;
    }
    
    .metric-card h3 {
        color: #808080;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        color: #ffffff;
        font-size: 1.8rem;
        margin: 0;
    }
    
    /* Chart container styling */
    .chart-container {
        background-color: #1f1f1f;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 1.5rem;
        border: 1px solid #333333;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1f1f1f;
    }
    
    .sidebar .sidebar-content {
        background-color: #1f1f1f;
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    
    p, div {
        color: #808080;
    }
    
    /* Plotly chart styling */
    .js-plotly-plot {
        background-color: #1f1f1f !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1f1f1f;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #E50914;
    }
    
    /* Footer styling */
    .footer {
        border-top: 1px solid #333333;
        padding-top: 1rem;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and Description
st.markdown("""
    <div class="header">
        <h1 style='text-align: center; color: #E50914; margin-bottom: 1rem; font-size: 2.5rem;'>
            Netflix Analytics Dashboard
        </h1>
        <div style='text-align: center; color: #808080; margin-bottom: 2rem;'>
            Explore Netflix's content library with interactive visualizations and insights. 
            Discover trends, patterns, and what makes a show successful on Netflix.
        </div>
    </div>
""", unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("netflix_titles.csv")
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        df['year_added'] = df['date_added'].dt.year
        df['month_added'] = df['date_added'].dt.month
        df['listed_in'] = df['listed_in'].astype(str)
        df['country'] = df['country'].fillna('Unknown')
        df['rating'] = df['rating'].fillna('Unknown')
        df['duration'] = df['duration'].fillna('0 min')
        df['duration_min'] = df['duration'].apply(lambda x: int(str(x).split()[0]) if 'min' in str(x) else 0)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/1920px-Netflix_2015_logo.svg.png", width=200)
    st.markdown("---")
    
    st.markdown("### Filters")
    
    # Content Type Filter
    content_type = st.multiselect(
        "Content Type",
        df['type'].dropna().unique(),
        default=df['type'].dropna().unique()
    )
    
    # Rating Filter
    selected_rating = st.multiselect(
        "Content Rating",
        df['rating'].dropna().unique(),
        default=df['rating'].dropna().unique()
    )
    
    # Country Filter
    all_countries = set()
    for countries in df['country'].dropna():
        for country in str(countries).split(', '):
            all_countries.add(country)
    all_countries = sorted(list(all_countries))
    selected_countries = st.multiselect(
        "Country",
        all_countries,
        default=all_countries
    )
    
    # Year Range Filter
    min_year = int(df['year_added'].min()) if not np.isnan(df['year_added'].min()) else 2000
    max_year = int(df['year_added'].max()) if not np.isnan(df['year_added'].max()) else 2023
    year_range = st.slider(
        "Year Added",
        min_year,
        max_year,
        (min_year, max_year)
    )
    
    # Duration Filter
    min_duration = int(df['duration_min'].min())
    max_duration = int(df['duration_min'].max())
    duration_range = st.slider(
        "Duration (minutes)",
        min_duration,
        max_duration,
        (min_duration, max_duration)
    )

# Filtering logic
mask_type = df['type'].isin(content_type)
mask_rating = df['rating'].isin(selected_rating)
mask_year = df['year_added'].between(year_range[0], year_range[1], inclusive='both')
mask_country = df['country'].apply(lambda x: any(country in str(x).split(', ') for country in selected_countries))
mask_duration = df['duration_min'].between(duration_range[0], duration_range[1], inclusive='both')
filtered_df = df[mask_type & mask_rating & mask_year & mask_country & mask_duration]

# Chart styling function
def update_chart_style(fig):
    fig.update_layout(
        paper_bgcolor='#1f1f1f',
        plot_bgcolor='#1f1f1f',
        font=dict(color='#ffffff'),
        title=dict(font=dict(color='#ffffff')),
        xaxis=dict(gridcolor='#333333', zerolinecolor='#333333'),
        yaxis=dict(gridcolor='#333333', zerolinecolor='#333333')
    )
    return fig

# Main content
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your filters.")
else:
    # Key Metrics
    st.markdown("### Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Total Titles</h3>
                <h2>{}</h2>
            </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        unique_countries = set()
        for countries in filtered_df['country']:
            for country in str(countries).split(', '):
                unique_countries.add(country)
        st.markdown("""
            <div class="metric-card">
                <h3>Unique Countries</h3>
                <h2>{}</h2>
            </div>
        """.format(len(unique_countries)), unsafe_allow_html=True)
    
    with col3:
        avg_duration = filtered_df['duration_min'].mean()
        st.markdown("""
            <div class="metric-card">
                <h3>Average Duration</h3>
                <h2>{:.1f} min</h2>
            </div>
        """.format(avg_duration), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card">
                <h3>Year Range</h3>
                <h2>{} - {}</h2>
            </div>
        """.format(year_range[0], year_range[1]), unsafe_allow_html=True)

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Content Analysis", "Genre Insights", "Geographic Analysis", "Advanced Analytics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            type_count = filtered_df['type'].value_counts().reset_index()
            type_count.columns = ['Type', 'Count']
            fig_type = px.pie(
                type_count,
                values='Count',
                names='Type',
                title='Content Type Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_type = update_chart_style(fig_type)
            st.plotly_chart(fig_type, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            rating_count = filtered_df['rating'].value_counts().reset_index()
            rating_count.columns = ['Rating', 'Count']
            fig_rating = px.bar(
                rating_count,
                x='Rating',
                y='Count',
                title='Content Rating Distribution',
                color='Rating',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_rating = update_chart_style(fig_rating)
            st.plotly_chart(fig_rating, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            yearly = filtered_df['year_added'].value_counts().sort_index().reset_index()
            yearly.columns = ['Year', 'Count']
            fig_years = px.line(
                yearly,
                x='Year',
                y='Count',
                title='Content Added Over Time',
                markers=True
            )
            fig_years.update_traces(line_color='#E50914')
            fig_years = update_chart_style(fig_years)
            st.plotly_chart(fig_years, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_duration = px.histogram(
                filtered_df,
                x='duration_min',
                title='Duration Distribution',
                nbins=30,
                color_discrete_sequence=['#E50914']
            )
            fig_duration = update_chart_style(fig_duration)
            st.plotly_chart(fig_duration, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            genre_series = filtered_df['listed_in'].str.split(', ', expand=True).stack()
            top_genres = genre_series.value_counts().head(10).reset_index()
            top_genres.columns = ['Genre', 'Count']
            fig_genre = px.bar(
                top_genres,
                x='Genre',
                y='Count',
                title='Top 10 Genres',
                color='Genre',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_genre = update_chart_style(fig_genre)
            st.plotly_chart(fig_genre, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown("### Popular Words in Titles")
            word_text = " ".join(filtered_df['title'].dropna().astype(str))
            if word_text.strip():
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='black',
                    stopwords=STOPWORDS,
                    colormap='Reds'
                ).generate(word_text)
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                st.pyplot(plt)
            else:
                st.info("No titles available to generate a word cloud.")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            country_series = filtered_df['country'].str.split(', ', expand=True).stack()
            top_countries = country_series.value_counts().head(10).reset_index()
            top_countries.columns = ['Country', 'Count']
            fig_countries = px.bar(
                top_countries,
                x='Country',
                y='Count',
                title='Top 10 Countries by Content',
                color='Country',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_countries = update_chart_style(fig_countries)
            st.plotly_chart(fig_countries, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            country_type = filtered_df.groupby(['country', 'type']).size().reset_index(name='count')
            country_type = country_type.sort_values('count', ascending=False).head(20)
            fig_country_type = px.bar(
                country_type,
                x='country',
                y='count',
                color='type',
                title='Content Type Distribution by Country',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_country_type = update_chart_style(fig_country_type)
            st.plotly_chart(fig_country_type, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_rating_duration = px.box(
                filtered_df,
                x='rating',
                y='duration_min',
                title='Duration Distribution by Rating',
                color='rating',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_rating_duration = update_chart_style(fig_rating_duration)
            st.plotly_chart(fig_rating_duration, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            type_rating = filtered_df.groupby(['type', 'rating']).size().reset_index(name='count')
            fig_type_rating = px.bar(
                type_rating,
                x='type',
                y='count',
                color='rating',
                title='Rating Distribution by Content Type',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_type_rating = update_chart_style(fig_type_rating)
            st.plotly_chart(fig_type_rating, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer" style='text-align: center;'>
        <p style='color: #808080;'>© 2024 Netflix Analytics Dashboard | Built with Streamlit</p>
        <p style='color: #808080;'>Data Source: Netflix Movies and TV Shows Dataset</p>
    </div>
""", unsafe_allow_html=True)
