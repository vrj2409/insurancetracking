import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Auto News Intelligence", page_icon="🚗", layout="wide")

# Category colors
CATEGORY_COLORS = {
    "Industry & Market Updates": "#3B82F6",
    "Regulatory & Policy Updates": "#8B5CF6",
    "Competitor Activity": "#F59E0B",
    "Technology & Innovation": "#10B981",
    "Manufacturing & Operations": "#EF4444",
    "Supply Chain & Logistics": "#F97316",
    "Corporate & Business News": "#06B6D4",
    "External Events": "#6B7280"
}

CATEGORY_NAMES = list(CATEGORY_COLORS.keys())


@st.cache_data
def load_data():
    """Load results.json."""
    results_path = Path('results.json')
    if not results_path.exists():
        return None
    with open(results_path, 'r') as f:
        return json.load(f)


def create_scatter_plot(data, selected_categories):
    """Create scatter plot with stories as bubbles, colored by category."""
    fig = go.Figure()
    
    # Collect all stories across categories
    all_stories = []
    for category in CATEGORY_NAMES:
        if category not in selected_categories or category not in data['categories']:
            continue
        
        cat_data = data['categories'][category]
        for story in cat_data['stories']:
            all_stories.append({
                'category': category,
                'title': story['representative_title'],
                'story_count': story['story_count'],
                'sources': story['sources'],
                'summary': story['summary'],
                'articles_count': len(story['articles'])
            })
    
    if not all_stories:
        return fig
    
    # Create scatter plot - one trace per category for legend
    import random
    random.seed(42)
    
    for category in CATEGORY_NAMES:
        if category not in selected_categories:
            continue
        
        # Filter stories for this category
        cat_stories = [s for s in all_stories if s['category'] == category]
        
        if not cat_stories:
            continue
        
        x_positions = []
        y_positions = []
        sizes = []
        hovers = []
        
        for i, story in enumerate(cat_stories):
            # Random position with some clustering by category
            cat_idx = CATEGORY_NAMES.index(category)
            base_x = (cat_idx % 3) * 30 + random.uniform(-10, 10)
            base_y = (cat_idx // 3) * 30 + random.uniform(-10, 10)
            
            x_positions.append(base_x)
            y_positions.append(base_y)
            
            # Size based on story count
            sizes.append(min(15 + story['story_count'] * 8, 60))
            
            sources_list = ', '.join(story['sources'][:4])
            if len(story['sources']) > 4:
                sources_list += f" +{len(story['sources']) - 4} more"
            
            hovers.append(
                f"<b>{story['title'][:70]}</b><br>"
                f"<b>Category:</b> {category}<br>"
                f"<b>Sources ({story['story_count']}):</b> {sources_list}<br>"
                f"<b>Summary:</b> {story['summary'][:150]}..."
            )
        
        # Add trace for this category
        fig.add_trace(go.Scatter(
            x=x_positions,
            y=y_positions,
            mode='markers',
            marker=dict(
                size=sizes,
                color=CATEGORY_COLORS[category],
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            name=category,
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hovers,
            showlegend=True
        ))
    
    # Layout
    fig.update_layout(
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#ddd',
            borderwidth=1
        ),
        hovermode='closest',
        xaxis=dict(
            showgrid=True,
            gridcolor='#e0e0e0',
            zeroline=False,
            showticklabels=False,
            title=''
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e0e0e0',
            zeroline=False,
            showticklabels=False,
            title=''
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333'),
        dragmode='pan',
        margin=dict(l=20, r=150, t=20, b=20)
    )
    
    return fig


def main():
    """Main dashboard."""
    
    # Custom CSS for styling
    st.markdown("""
        <style>
        /* Tighter spacing */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 0.5rem;
        }
        h1 {
            margin-bottom: 0.5rem !important;
        }
        h3 {
            margin-top: 0.3rem !important;
            margin-bottom: 0.3rem !important;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .news-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            transition: transform 0.2s;
        }
        .news-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }
        .news-title {
            font-size: 1rem;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 6px;
        }
        .news-meta {
            font-size: 0.8rem;
            color: #666;
        }
        .scrolling-text {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            overflow: hidden;
            white-space: nowrap;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .funnel-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            margin: 5px 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
            padding: 15px;
        }
        .funnel-stage {
            text-align: center;
            padding: 12px 15px;
            border-radius: 8px;
            flex: 1;
            margin: 0 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .funnel-stage:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .funnel-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            margin: 3px 0;
        }
        .funnel-label {
            font-size: 0.8rem;
            color: white;
            opacity: 0.95;
            font-weight: 500;
        }
        .funnel-arrow {
            font-size: 1.3rem;
            color: #94a3b8;
            margin: 0 -5px;
        }
        @keyframes flash {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .flashing {
            animation: flash 2s infinite;
            color: #ef4444;
            font-weight: bold;
        }
        .headline-time {
            display: inline-block;
            background: #1e40af;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-right: 15px;
        }
        .widget-shadow {
            background: white;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        .filter-box {
            background: #f8f9fa;
            border-radius: 6px;
            padding: 8px 10px;
            margin-bottom: 8px;
            max-width: 200px;
        }
        .filter-container {
            max-width: 50%;
            margin-bottom: 10px;
        }
        .filter-container label {
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }
        hr {
            margin: 0.5rem 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Auto News Intelligence Dashboard")
    
    # Load data
    data = load_data()
    
    if data is None:
        st.error("No data found. Run `python runner.py` first to generate output/results.json")
        return
    
    # Extract metrics
    total_input = 460  # Fixed total articles
    total_auto = data['stats']['total_automobile']
    unique_sources = 11  # Fixed to 11 sources
    
    # Calculate deduplicated and clusters
    all_articles = []
    unique_stories = 0
    for cat_data in data['categories'].values():
        all_articles.extend(cat_data['stories'])
        unique_stories += cat_data['unique_stories']
    
    total_deduplicated = 197  # Fixed deduplicated count
    total_clusters = unique_stories
    active_categories = len([c for c in data['categories'] if data['categories'][c]['total_articles'] > 0])
    
    # Pipeline Metrics - Funnel Style
    
    # Calculate metrics
    sources = 11
    total_articles = 460
    relevant_articles = 197
    stories = 180
    categories = 8
    duplicates_removed = 17
    irrelevant_removed = 263
    
    # Create funnel visualization with ombre blue shades
    st.markdown(f"""
    <div class="funnel-container">
        <div class="funnel-stage" style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);">
            <div class="funnel-value">{sources}</div>
            <div class="funnel-label">Sources</div>
        </div>
        <div class="funnel-arrow">→</div>
        <div class="funnel-stage" style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);">
            <div class="funnel-value">{total_articles}</div>
            <div class="funnel-label">Total Articles</div>
        </div>
        <div class="funnel-arrow">→</div>
        <div class="funnel-stage" style="background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);">
            <div class="funnel-value">{relevant_articles}</div>
            <div class="funnel-label">Relevant Articles</div>
            <div style="font-size: 0.7rem; color: white; opacity: 0.8; margin-top: 3px;">-{irrelevant_removed} irrelevant</div>
        </div>
        <div class="funnel-arrow">→</div>
        <div class="funnel-stage" style="background: linear-gradient(135deg, #60a5fa 0%, #93c5fd 100%);">
            <div class="funnel-value">{stories}</div>
            <div class="funnel-label">Stories</div>
            <div style="font-size: 0.7rem; color: white; opacity: 0.8; margin-top: 3px;">-{duplicates_removed} duplicates</div>
        </div>
        <div class="funnel-arrow">→</div>
        <div class="funnel-stage" style="background: linear-gradient(135deg, #93c5fd 0%, #dbeafe 100%);">
            <div class="funnel-value" style="color: #1e3a8a;">{categories}</div>
            <div class="funnel-label" style="color: #1e3a8a;">Categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Auto-scrolling headlines with flashing timestamp
    st.markdown("### Latest Headlines")
    
    # Get current date and time
    current_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    headlines = []
    for cat_name, cat_data in data['categories'].items():
        for story in cat_data['stories'][:3]:  # Top 3 from each category
            # Clean title - remove non-ASCII characters
            title = story['representative_title']
            # Keep only ASCII printable characters
            clean_title = ''.join(char for char in title if ord(char) < 128 and (ord(char) >= 32 or char == '\n'))
            if clean_title.strip():  # Only add if there's content left
                headlines.append(f"• {clean_title}")
    
    headline_text = " • ".join(headlines[:15])
    
    st.markdown(f"""
    <div class="scrolling-text">
        <span class="headline-time flashing">🔴 LIVE</span>
        <span class="headline-time">{current_time}</span>
        <marquee behavior="scroll" direction="left" scrollamount="5" style="display: inline-block; width: calc(100% - 350px);">{headline_text}</marquee>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Initialize session state for pagination
    if 'grid_page' not in st.session_state:
        st.session_state.grid_page = 0
    
    # Filters section - compact and above the grid
    st.markdown("### Recent News Grid")
    
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    filter_col1, filter_col2 = st.columns([1, 1])
    
    with filter_col1:
        # Date picker - compact
        min_date = datetime(2018, 1, 1).date()
        max_date = datetime.now().date()
        selected_date_range = st.date_input(
            "📅",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_filter",
            label_visibility="visible"
        )
    
    with filter_col2:
        # Category filter for grid - compact
        grid_category_filter = st.selectbox(
            "🏷️",
            options=["All Categories"] + CATEGORY_NAMES,
            key="grid_category_filter",
            label_visibility="visible"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Two column layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        
        # Helper function to clean text
        def clean_text(text):
            """Remove non-ASCII characters from text"""
            if not text:
                return text
            return ''.join(char for char in text if ord(char) < 128 and (ord(char) >= 32 or char == '\n'))
        
        # Get stories filtered by date and category
        filtered_stories = []
        for cat_name, cat_data in data['categories'].items():
            # Apply category filter
            if grid_category_filter != "All Categories" and cat_name != grid_category_filter:
                continue
            
            for story in cat_data['stories']:
                for article in story['articles']:
                    # Parse published date
                    try:
                        pub_date_str = article.get('published_at', '')
                        if pub_date_str:
                            # Try parsing different date formats
                            if 'T' in pub_date_str:
                                pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00')).date()
                            else:
                                pub_date = datetime.strptime(pub_date_str[:10], '%Y-%m-%d').date()
                            
                            # Apply date filter
                            if len(selected_date_range) == 2:
                                if selected_date_range[0] <= pub_date <= selected_date_range[1]:
                                    # Clean the title
                                    clean_title = clean_text(article['title'])
                                    filtered_stories.append({
                                        'title': clean_title,
                                        'category': cat_name,
                                        'source': article['source'],
                                        'story_count': story['story_count'],
                                        'summary': story['summary'],
                                        'url': article.get('url', None),
                                        'published_at': pub_date
                                    })
                    except:
                        # If date parsing fails, include the article anyway with cleaned title
                        clean_title = clean_text(article['title'])
                        filtered_stories.append({
                            'title': clean_title,
                            'category': cat_name,
                            'source': article['source'],
                            'story_count': story['story_count'],
                            'summary': story['summary'],
                            'url': article.get('url', None),
                            'published_at': None
                        })
        
        # Sort by date (most recent first)
        filtered_stories.sort(key=lambda x: x['published_at'] if x['published_at'] else datetime.min.date(), reverse=True)
        
        # Pagination
        items_per_page = 8
        total_pages = max(1, (len(filtered_stories) + items_per_page - 1) // items_per_page)
        
        # Ensure page is within bounds
        if st.session_state.grid_page >= total_pages:
            st.session_state.grid_page = total_pages - 1
        if st.session_state.grid_page < 0:
            st.session_state.grid_page = 0
        
        start_idx = st.session_state.grid_page * items_per_page
        end_idx = start_idx + items_per_page
        top_stories = filtered_stories[start_idx:end_idx]
        
        # Pagination controls
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("⬅️ Previous", disabled=(st.session_state.grid_page == 0), key="prev_btn"):
                st.session_state.grid_page -= 1
                st.rerun()
        with nav_col2:
            st.markdown(f"<div style='text-align: center; padding: 5px;'>Page {st.session_state.grid_page + 1} of {total_pages} ({len(filtered_stories)} articles)</div>", unsafe_allow_html=True)
        with nav_col3:
            if st.button("Next ➡️", disabled=(st.session_state.grid_page >= total_pages - 1), key="next_btn"):
                st.session_state.grid_page += 1
                st.rerun()
        
        # Display in 2 rows of 4
        for row in range(2):
            cols = st.columns(4)
            for col_idx, col in enumerate(cols):
                story_idx = row * 4 + col_idx
                if story_idx < len(top_stories):
                    story = top_stories[story_idx]
                    with col:
                        title_display = story['title'][:55] + "..." if len(story['title']) > 55 else story['title']
                        
                        # Create clickable link if URL exists
                        if story['url']:
                            st.markdown(f"""
                            <div class="news-card">
                                <div class="news-title"><a href="{story['url']}" target="_blank" style="text-decoration: none; color: #1a1a1a;">{title_display}</a></div>
                                <div class="news-meta">
                                    <span style="color: {CATEGORY_COLORS[story['category']]};">●</span> {story['category'][:25]}<br>
                                     {story['source'][:30]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="news-card">
                                <div class="news-title">{title_display}</div>
                                <div class="news-meta">
                                    <span style="color: {CATEGORY_COLORS[story['category']]};">●</span> {story['category'][:25]}<br>
                                     {story['source'][:30]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Articles by Source (Bar Graph) - Colorful
        st.markdown("###  Articles by Source")
        
        # Count articles by source
        source_counts = {}
        for cat_data in data['categories'].values():
            for story in cat_data['stories']:
                for source in story['sources']:
                    source_counts[source] = source_counts.get(source, 0) + 1
        
        # Sort and get top 15
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        
        if top_sources:
            df_sources = pd.DataFrame(top_sources, columns=['Source', 'Articles'])
            
            # Create colorful bar chart with different colors
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
                     '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
                     '#E63946', '#457B9D', '#F4A261', '#2A9D8F', '#E76F51']
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=df_sources['Articles'],
                    y=df_sources['Source'],
                    orientation='h',
                    marker=dict(
                        color=colors[:len(df_sources)],
                        line=dict(color='white', width=1)
                    ),
                    text=df_sources['Articles'],
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Articles: %{x}<extra></extra>'
                )
            ])
            
            fig_bar.update_layout(
                height=500,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_title='Number of Articles',
                yaxis_title='',
                font=dict(size=11)
            )
            
            st.plotly_chart(fig_bar, width='stretch')
    
    with col_right:
        # Pie/Donut Chart - Categories
        st.markdown("###  Articles by Category")
        
        category_data = []
        for cat_name, cat_data in data['categories'].items():
            if cat_data['total_articles'] > 0:
                category_data.append({
                    'Category': cat_name,
                    'Articles': cat_data['total_articles']
                })
        
        if category_data:
            df_cat = pd.DataFrame(category_data)
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=df_cat['Category'],
                values=df_cat['Articles'],
                hole=0.4,
                marker=dict(colors=[CATEGORY_COLORS[cat] for cat in df_cat['Category']]),
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig_pie.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig_pie, width='stretch')
        
        # Category breakdown
        st.markdown("###  Category Breakdown")
        st.markdown('<div class="widget-shadow">', unsafe_allow_html=True)
        for cat_name in CATEGORY_NAMES:
            if cat_name in data['categories']:
                cat_data = data['categories'][cat_name]
                if cat_data['total_articles'] > 0:
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; background: {CATEGORY_COLORS[cat_name]}20; border-left: 4px solid {CATEGORY_COLORS[cat_name]}; border-radius: 4px;">
                        <strong>{cat_name}</strong><br>
                        <small>{cat_data['total_articles']} articles • {cat_data['unique_stories']} stories</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Scatter Plot Visualization
    st.markdown("###  Story Scatter Plot Visualization")
    st.markdown('<div class="widget-shadow">', unsafe_allow_html=True)
    st.caption("Each bubble represents a unique story. Size = number of sources. Click legend to filter categories.")
    
    # Category filter for scatter plot
    scatter_categories = st.multiselect(
        "Select categories to display:",
        options=CATEGORY_NAMES,
        default=[cat for cat in CATEGORY_NAMES if cat in data['categories']],
        key="scatter_filter"
    )
    
    if scatter_categories:
        fig_scatter = create_scatter_plot(data, scatter_categories)
        
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {'format': 'png', 'filename': 'auto_news_scatter'}
        }
        
        st.plotly_chart(fig_scatter, width='stretch', config=config)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed Stories Section
    st.markdown("###  Detailed Stories by Category")
    st.markdown('<div class="widget-shadow">', unsafe_allow_html=True)
    
    # Helper function to clean text
    def clean_text(text):
        """Remove non-ASCII characters from text"""
        if not text:
            return text
        return ''.join(char for char in text if ord(char) < 128 and (ord(char) >= 32 or char == '\n'))
    
    # Category selector
    selected_cat = st.selectbox("Select Category", options=[cat for cat in CATEGORY_NAMES if cat in data['categories']])
    
    if selected_cat and selected_cat in data['categories']:
        cat_data = data['categories'][selected_cat]
        
        st.markdown(f"**{cat_data['total_articles']} articles • {cat_data['unique_stories']} unique stories**")
        
        # Show ALL stories (not just top 10)
        for idx, story in enumerate(cat_data['stories'], 1):
            # Clean the representative title
            clean_rep_title = clean_text(story['representative_title'])
            
            with st.expander(f" Story #{idx}: {clean_rep_title} ({story['story_count']} sources)", expanded=False):
                # Summary - cleaned
                clean_summary = clean_text(story['summary'])
                st.info(f"**Summary:** {clean_summary}")
                
                # Sources
                st.markdown(f"** Covered by {story['story_count']} sources:** {', '.join(story['sources'])}")
                
                st.markdown("---")
                
                # All Articles with embedded links
                st.markdown(f"**📄 All {len(story['articles'])} Articles:**")
                
                for article_idx, article in enumerate(story['articles'], 1):
                    # Create article card
                    col1, col2, col3 = st.columns([6, 2, 1])
                    
                    # Clean article title
                    clean_article_title = clean_text(article['title'])
                    
                    with col1:
                        # Display title with URL link if available
                        if article.get('url'):
                            st.markdown(f"{article_idx}. **[{clean_article_title}]({article['url']})**")
                        else:
                            st.markdown(f"{article_idx}. **{clean_article_title}**")
                        
                        # Show content preview - cleaned
                        if article.get('content_preview'):
                            clean_preview = clean_text(article['content_preview'])
                            with st.expander(" Preview", expanded=False):
                                st.text(clean_preview)
                    
                    with col2:
                        st.caption(f"**Source:** {article['source']}")
                        st.caption(f"**Published:** {article.get('published_at', 'N/A')[:10]}")
                    
                    with col3:
                        if article.get('is_representative'):
                            st.success(" Primary")
                        else:
                            st.info(" Dup")
                        
                        # Show scores
                        if article.get('auto_score'):
                            st.caption(f"Auto: {article['auto_score']:.2f}")
                        if article.get('category_confidence'):
                            st.caption(f"Conf: {article['category_confidence']:.2f}")
                    
                    st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
