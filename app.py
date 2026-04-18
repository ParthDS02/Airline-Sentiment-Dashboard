"""
Airline Sentiment Dashboard
A simple Streamlit app to analyze Twitter sentiment about US airlines.
Data source: Twitter US Airline Sentiment dataset (Feb 2015)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Page config - do this first before anything else
st.set_page_config(page_title="Airline Sentiment Analysis", page_icon="✈️", layout="wide")

# Main title
st.title("✈️ Airline Sentiment Analysis Dashboard")
st.markdown("*Analyzing customer opinions from Twitter about US Airlines*")
st.divider()

# Load the data - using @st.cache_data so it only loads once
@st.cache_data
def load_data():
    """
    Load and prepare tweet data.
    The data has tweet text, sentiment labels, and airline info.
    """
    data = pd.read_csv("data/Tweets.csv")
    # Convert to datetime so we can filter by time
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

# Get the data
data = load_data()


# Count sentiments (we'll use these in different sections)
negative_count = len(data[data['airline_sentiment'] == 'negative'])
neutral_count = len(data[data['airline_sentiment'] == 'neutral'])
positive_count = len(data[data['airline_sentiment'] == 'positive'])


# ============================================================================
# SIDEBAR - Navigation and controls
# ============================================================================

st.sidebar.title("🎛️ Navigation")

# Main navigation - pick which section to view
section = st.sidebar.radio(
    "Choose Analysis:",
    [
        "📊 Overall Sentiment",
        "🛫 Airline Comparison", 
        "🗺️ Geographic Analysis",
        "☁️ Word Cloud",
        "🎲 Random Tweets"
    ],
    help="Select different analyses to view"
)

st.sidebar.divider()
st.sidebar.info("""
💡 **Tip:** Use the radio buttons above to explore different views of the data.
Each section shows a different aspect of airline sentiment.
""")
st.sidebar.caption("**Created by:** Parth B Mistry")


# ============================================================================
# MAIN AREA - Show selected section
# ============================================================================

# --- SECTION 1: Overall Sentiment ---
if section == "📊 Overall Sentiment":
    st.header("📊 Overall Sentiment Distribution")
    st.markdown("*How do people feel about airlines on Twitter?*")
    
    # Quick stats - only in this section
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Tweets", f"{len(data):,}")
    col2.metric("Positive", f"{positive_count:,} ({(positive_count/len(data)*100):.1f}%)")
    col3.metric("Negative", f"{negative_count:,} ({(negative_count/len(data)*100):.1f}%)")
    
    st.divider()
    
    # Let user pick chart type
    chart_type = st.radio("Chart Style:", ['Bar Chart', 'Pie Chart'], horizontal=True)
    
    # Prepare data for chart
    sentiment_count = data['airline_sentiment'].value_counts()
    sentiment_df = pd.DataFrame({
        'Sentiment': sentiment_count.index, 
        'Tweets': sentiment_count.values
    })
    
    # Show the chart based on user's choice
    if chart_type == "Bar Chart":
        fig = px.bar(
            sentiment_df, 
            x='Sentiment', 
            y='Tweets', 
            color='Tweets',
            title="Sentiment Breakdown",
            color_continuous_scale='RdYlGn_r',
            text='Tweets'
        )
        fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    else:
        fig = px.pie(
            sentiment_df, 
            values='Tweets', 
            names='Sentiment',
            title="Sentiment Distribution",
            color_discrete_map={
                'positive': '#00cc96',
                'neutral': '#ffa15a', 
                'negative': '#ef553b'
            }
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show insights
    with st.expander("💡 Key Insights"):
        st.markdown(f"""
        - **Most tweets are negative** ({negative_count:,} out of {len(data):,})
        - Only {(positive_count/len(data)*100):.1f}% of tweets are positive
        - This suggests significant customer service issues across airlines
        """)

# --- SECTION 2: Airline Comparison ---
elif section == "🛫 Airline Comparison":
    st.header("🛫 Airline-by-Airline Comparison")
    st.markdown("*Which airlines get the most complaints?*")
    
    # Let user pick airlines to compare
    airlines = st.multiselect(
        'Select airlines to compare:', 
        ['US Airways', 'American', 'United', 'Southwest', 'Delta', 'Virgin America'],
        default=['United', 'Delta', 'Virgin America'],  # Show some by default
        help="Pick at least one airline"
    )
    
    if len(airlines) > 0:
        # Filter to selected airlines
        filtered = data[data.airline.isin(airlines)]
        
        # Show two views side by side
        col1, col2 = st.columns(2)
        
        with col1:
            # Grouped bar chart
            fig1 = px.histogram(
                filtered, 
                x='airline', 
                color='airline_sentiment',
                barmode='group',
                title="Sentiment Count by Airline",
                color_discrete_map={
                    'positive': '#00cc96',
                    'neutral': '#ffa15a',
                    'negative': '#ef553b'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Stacked percentage chart
            fig2 = px.histogram(
                filtered, 
                x='airline',
                color='airline_sentiment',
                barnorm='percent',
                title="Sentiment % by Airline",
                color_discrete_map={
                    'positive': '#00cc96',
                    'neutral': '#ffa15a',
                    'negative': '#ef553b'
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Show summary table
        with st.expander("📋 View Summary Table"):
            summary = filtered.groupby(['airline', 'airline_sentiment']).size().unstack(fill_value=0)
            summary['Total'] = summary.sum(axis=1)
            st.dataframe(summary)
    else:
        st.warning("👆 Please select at least one airline to see the comparison")

# --- SECTION 3: Geographic Analysis ---
elif section == "🗺️ Geographic Analysis":
    st.header("🗺️ Where Are People Tweeting From?")
    st.markdown("*See tweet locations across the USA by hour*")
    
    # Hour slider
    hour = st.slider("Select hour of day:", 0, 23, 12, 
                     help="Move the slider to see tweets at different times")
    
    # Filter by the selected hour
    map_data = data[data['tweet_created'].dt.hour == hour]
    
    # Show count
    st.metric("Tweets in this hour", f"{len(map_data):,}", 
              f"Between {hour}:00 and {(hour + 1) % 24}:00")
    
    # Show the map
    st.map(map_data)
    
    # Option to see raw data
    if st.checkbox("📄 Show raw data for this hour"):
        st.dataframe(
            map_data[['airline', 'airline_sentiment', 'text', 'tweet_created', 'latitude', 'longitude']],
            use_container_width=True
        )

# --- SECTION 4: Word Cloud ---
elif section == "☁️ Word Cloud":
    st.header("☁️ Most Common Words in Tweets")
    st.markdown("*What are people actually saying?*")
    
    # Pick sentiment
    wc_sentiment = st.radio(
        'Choose sentiment type:', 
        ('positive', 'neutral', 'negative'),
        horizontal=True
    )
    
    # Generate button
    if st.button("🔄 Generate Word Cloud", type="primary"):
        with st.spinner("Creating word cloud..."):
            # Filter tweets by sentiment
            wc_data = data[data['airline_sentiment'] == wc_sentiment]
            
            st.info(f"Using {len(wc_data):,} {wc_sentiment} tweets")
            
            # Combine all tweet text
            all_words = ' '.join(wc_data['text'])
            
            # Clean up - remove URLs, mentions, and retweet markers
            clean_words = ' '.join([
                word for word in all_words.split() 
                if 'http' not in word 
                and not word.startswith('@') 
                and word != 'RT'
            ])
            
            # Generate the cloud with colors based on sentiment
            color_map = {
                'positive': 'Greens',
                'neutral': 'Greys', 
                'negative': 'Reds'
            }
            
            wordcloud = WordCloud(
                stopwords=STOPWORDS,
                background_color='white',
                width=1200,
                height=600,
                colormap=color_map[wc_sentiment]
            ).generate(clean_words)
            
            # Display it
            fig, ax = plt.subplots(figsize=(15, 7))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
            with st.expander("💡 How to read this"):
                st.markdown("""
                - **Bigger words** appear more frequently in tweets
                - Common words like "the", "and" are automatically removed
                - URLs and @mentions are filtered out
                - This helps you quickly see main topics and concerns
                """)

# --- SECTION 5: Random Tweets ---
elif section == "🎲 Random Tweets":
    st.header("🎲 See What People Are Actually Saying")
    st.markdown("*Random sample of real tweets from customers*")
    
    # Pick sentiment
    sentiment_choice = st.radio(
        'Choose sentiment type:', 
        ('positive', 'neutral', 'negative'),
        horizontal=True
    )
    
    # Show multiple random tweets
    num_tweets = st.slider("How many tweets to show?", 1, 10, 5)
    
    # Get random tweets
    sample_tweets = data.query('airline_sentiment == @sentiment_choice')[['airline', 'text', 'tweet_created']].sample(n=num_tweets)
    
    # Display each tweet nicely
    for idx, row in sample_tweets.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{row['airline']}**")
                st.caption(row['tweet_created'].strftime('%Y-%m-%d'))
            with col2:
                # Color code by sentiment
                if sentiment_choice == 'positive':
                    st.success(f"💚 {row['text']}")
                elif sentiment_choice == 'negative':
                    st.error(f"❤️ {row['text']}")
                else:
                    st.info(f"💙 {row['text']}")
        st.divider()
    
    # Refresh button
    if st.button("🔄 Show Different Tweets"):
        st.rerun()

# Footer - always visible
st.divider()
st.caption("📊 Data: Twitter US Airline Sentiment (February 2015) | Source: Kaggle")