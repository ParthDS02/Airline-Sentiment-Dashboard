import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

st.title("Decoding Public Opinion: Sentiment Analysis of U.S. Airlines Tweets")
st.sidebar.title("Sentiment Analysis of Twits about U.S.Airlines")

st.markdown(" This application is a streamlit Dashboard to analyze of Twits 🐦")
st.sidebar.markdown(" This application is a streamlit Dashboard to analyze of Twits 🐦")

# Use relative path - data is now in data folder
DATA_URL = "data/Tweets.csv"

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()

st.sidebar.subheader("Show Random Tweet")
random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
st.sidebar.markdown(data.query('airline_sentiment == @random_tweet')[["text"]].sample(n =1).iat[0,0])

st.sidebar.markdown("### Number of Tweets by Sentiment")
select = st.sidebar.selectbox('Visualization', ['Histogram', 'Pie Chart'], key = '1')
sentiment_count = data['airline_sentiment']. value_counts()
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of Tweets by sentiment")
    if select == "Histogram":
        fig = px.bar(sentiment_count, x = 'Sentiment',  y = 'Tweets', color = 'Tweets', height = 500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)

st.sidebar.subheader("When and where are user tweeting from?")
st.sidebar.markdown("You can directly enter the number into the box.")
hour = st.sidebar.number_input("Hour of day",min_value = 1, max_value = 24)
modified_data = data[data['tweet_created'].dt.hour == hour]
if not st.sidebar.checkbox("Close",True, key='checkbox_1'):
    st.markdown("### Tweets  locations based on the time of dat")
    st.markdown("%i tweets between %i:00 and %i:00" % (len(modified_data), hour, (hour + 1) % 24))
    st.map(modified_data)
    if st.sidebar.checkbox("Show raw data", False):
        st.write(modified_data)

st.sidebar.subheader("Breakdown airline tweets by sentiment")
choice = st.sidebar.multiselect('Pick airlines', ('US Airways','American', 'United', 'Southwest', 'Delta', 'Virgin America'), key = '0')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)] #choice_data is sub set of original dataset
    fig_choice = px.histogram(choice_data, x ='airline', y = 'airline_sentiment', histfunc= 'count', color = 'airline_sentiment', facet_col= 'airline_sentiment', labels={'airline_sentiment: tweets'}, height=600, width=800)
    st.plotly_chart(fig_choice)



st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio('Display word cloud for what sentiment?', ('positive','negative', 'neutral'))

if not st.sidebar.checkbox("Close", True, key = 3):
    st.header(f'Word cloud for {word_sentiment} sentiment')
    df = data[data['airline_sentiment']==word_sentiment] # Filter data based on sentiment
    words = ' '.join(df['text']) # Join all the tweet text into a single string
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@')and word != 'RT']) # Remove unwanted words (URLs, mentions, and RTs)
    wordcloud = WordCloud(stopwords= STOPWORDS, background_color='white', height= 640, width=800).generate(processed_words) # Generate the word cloud
    
    # Create a figure and plot the word cloud on it
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot(fig)