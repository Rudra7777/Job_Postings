import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set page config for better layout
st.set_page_config(
    page_title="LinkedIn Jobs Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for compact layout
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chart-container {
        background: white;
        padding: 0.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 0.5rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    # URL to your Google Sheets file (export format for XLSX)
    sheet_url = 'https://docs.google.com/spreadsheets/d/1vY51icoW9eiMsFHGeFmpb0SAp5XOsZGL/export?format=xlsx'
    
    try:
        df = pd.read_excel(sheet_url)
    except Exception as e:
        st.error(f"Failed to load data from Google Sheets: {e}")
        st.stop()
    
    # Calculate derived columns
    df['avgSalary'] = (df['minimumSalary'] + df['maximumSalary']) / 2
    df['avgExperience'] = (df['minimumExperience'] + df['maximumExperience']) / 2
    
    def categorize_experience(exp):
        if exp <= 1: return 'Fresher (0-1 years)'
        elif exp <= 3: return 'Entry Level (1-3 years)'
        elif exp <= 5: return 'Mid Level (3-5 years)'
        elif exp <= 10: return 'Senior Level (5-10 years)'
        else: return 'Expert Level (10+ years)'
    
    df['experienceCategory'] = df['avgExperience'].apply(categorize_experience)
    return df

def create_wordcloud(text_data):
    """Create word cloud from text data"""
    if text_data.empty or len(text_data) == 0:
        return None
    
    all_text = ' '.join(str(text) for text in text_data if pd.notna(text))
    words = re.findall(r'\b\w+\b', all_text.lower())
    stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'skills', 'skill', 'experience', 'required', 'years', 'year', 'work'}
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    if not words:
        return None
    
    wordcloud = WordCloud(width=600, height=300, background_color='white', 
                         max_words=80, colormap='viridis').generate(' '.join(words))
    return wordcloud

def create_chart1(df):
    """Top 10 Job Titles by Openings"""
    fig, ax = plt.subplots(figsize=(6, 4))
    title_counts = df['title'].value_counts().head(10)
    
    bars = ax.barh(range(len(title_counts)), title_counts.values, color='#1f77b4', alpha=0.8)
    ax.set_yticks(range(len(title_counts)))
    ax.set_yticklabels(title_counts.index, fontsize=8)
    ax.set_xlabel('Openings', fontsize=9)
    ax.set_title('Top 10 Job Titles', fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(title_counts.values):
        ax.text(v + 2, i, f'{v:,}', va='center', fontsize=8)
    
    plt.tight_layout()
    return fig

def create_chart2(df):
    """Top 10 Cities with Most Job Listings"""
    fig, ax = plt.subplots(figsize=(6, 4))
    city_counts = df['location'].value_counts().head(10)
    
    bars = ax.barh(range(len(city_counts)), city_counts.values, color='#ff7f0e', alpha=0.8)
    ax.set_yticks(range(len(city_counts)))
    ax.set_yticklabels(city_counts.index, fontsize=8)
    ax.set_xlabel('Job Listings', fontsize=9)
    ax.set_title('Top 10 Cities', fontsize=11, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(city_counts.values):
        ax.text(v + max(city_counts.values)*0.01, i, f'{v:,}', va='center', fontsize=8)
    
    plt.tight_layout()
    return fig

def create_chart3(df):
    """In-demand Skills Word Cloud"""
    fig, ax = plt.subplots(figsize=(10, 4))
    skills_text = df['tagsAndSkills'].dropna()
    wordcloud = create_wordcloud(skills_text)
    
    if wordcloud:
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('In-demand Skills', fontsize=11, fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'No skills data available', 
                ha='center', va='center', fontsize=12, transform=ax.transAxes)
        ax.axis('off')
    
    plt.tight_layout()
    return fig

def create_chart6(df):
    """Top 10 Companies by Average Salary"""
    fig, ax = plt.subplots(figsize=(6, 4))
    company_salary = df.groupby('companyName')['avgSalary'].mean().round(0)
    company_salary = company_salary.sort_values(ascending=False).head(10)
    
    bars = ax.barh(range(len(company_salary)), company_salary.values, color='#2ca02c', alpha=0.8)
    ax.set_yticks(range(len(company_salary)))
    ax.set_yticklabels([name[:15] + '...' if len(name) > 15 else name for name in company_salary.index], fontsize=7)
    ax.set_xlabel('Avg Salary (₹)', fontsize=9)
    ax.set_title('Top 10 Companies\nby Salary', fontsize=10, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(company_salary.values):
        ax.text(v + 1000, i, f'₹{v/1000:.0f}k', va='center', fontsize=7)
    
    plt.tight_layout()
    return fig

def create_chart8(df):
    """Fresher vs Experienced Roles"""
    fig, ax = plt.subplots(figsize=(6, 4))
    fresher_exp = df['experienceCategory'].value_counts()
    
    wedges, texts, autotexts = ax.pie(fresher_exp.values, labels=fresher_exp.index, 
                                      autopct='%1.0f%%', startangle=90, 
                                      colors=['#d62728', '#ff9896', '#98df8a', '#ffbb78', '#c5b0d5'])
    ax.set_title('Fresher vs Experienced Roles', fontsize=11, fontweight='bold')
    ax.axis('equal')
    
    # Make labels smaller
    for text in texts:
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_fontsize(8)
    
    plt.tight_layout()
    return fig

# Main app
def main():
    # Load data
    df = load_data()
    
    # Header with KPIs
    st.markdown('<h1 class="main-header">💼 LinkedIn Jobs Dashboard</h1>', unsafe_allow_html=True)
    
    # KPIs in a compact row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Total Jobs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_salary = df['avgSalary'].mean()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">₹{avg_salary/1000:.0f}k</div>
            <div class="metric-label">Avg Salary</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_exp = df['avgExperience'].mean()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{avg_exp:.1f}</div>
            <div class="metric-label">Avg Exp (yrs)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        top_city = df['location'].value_counts().index[0]
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{top_city}</div>
            <div class="metric-label">Top City</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        fresher_pct = (len(df[df['experienceCategory'] == 'Fresher (0-1 years)']) / len(df)) * 100
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{fresher_pct:.0f}%</div>
            <div class="metric-label">Fresher Jobs</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts in compact layout
    # Row 1: Chart 1 and Chart 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig1 = create_chart1(df)
        st.pyplot(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig2 = create_chart2(df)
        st.pyplot(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Chart 3 (full width)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig3 = create_chart3(df)
    st.pyplot(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 3: Chart 6 and Chart 8
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig6 = create_chart6(df)
        st.pyplot(fig6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig8 = create_chart8(df)
        st.pyplot(fig8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption("*Dashboard created with Streamlit • Data: LinkedIn Jobs India*")

if __name__ == "__main__":
    main()