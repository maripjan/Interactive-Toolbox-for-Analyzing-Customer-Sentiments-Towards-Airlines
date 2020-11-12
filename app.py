import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

### Page Title
st.title("Interactive Toolbox for Sentiment Analysis of Airline Customers")

## Project Description
st.markdown("""
    <p>This application is an interactive dashboard which uses Twitter data to analyze sentiments of U.S. cusomters towards airline firms. 
    The app was built using Python's relatively new <a href="https://streamlit.io"> Streamlit </a> Web Framework. </p>

    <h4> <b>Project Description</b>: </h4>
    
    <i>Dataset that I used here is an open-source data and is freely available at 
    <a href="https://www.kaggle.com/crowdflower/twitter-airline-sentiment"> Kaggle </a>.
     The motivation behind creating this project was to create a simple but user-friendly application that will allow people
     with no programming experience to perform Exploratory Data Analysis.
    </i>
        """, unsafe_allow_html=True)

st.markdown(" <hr>", unsafe_allow_html=True)

st.sidebar.title("Discover what customers think of major U.S. airline companies")

DATA_URL = ('D:/Python projects/Airlines Sentiment Analysis/Tweets.csv')

@st.cache(persist=True)   ##This decorator cashes loaded data in order to avoid overloading RAM and CPU.
def load_data():
    data = pd.read_csv(DATA_URL)
    ## COnvert some columns into Python datetime format
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

## Load dataset
data = load_data()

## Widget for choosing an airline firm
airline = st.sidebar.selectbox(label = "Choose an airline", options = (np.append(data['airline'].unique(),['All']) ))

## Widget for choosing customers' sentiment
sentiment_type = st.sidebar.radio("Customer sentiments", ('positive', 'neutral', 'negative'))

### Narrow down dataset such that only rows containing selected airline firm and selcted sentiment type are chosen
def selected_subset():
    if airline == "All":
        return data.query('airline_sentiment == @sentiment_type')
    else:
         return data.query('airline_sentiment == @sentiment_type & airline == @airline')

### Show A Word Cloud containing most frequent words for a given sentiment and a given airline firm
if st.sidebar.checkbox("Show Word Cloud")==True:
    st.subheader(f'Most frequently used words for a {sentiment_type} sentiment when {airline} is mentioned')    
    wordcloud_df = selected_subset() #data.query('airline_sentiment == @sentiment_type & airline == @airline')
    words = ' '.join(wordcloud_df['text'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    wordcloud = WordCloud(stopwords = STOPWORDS, background_color = 'white', height = 500, width = 750).generate(processed_words)
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot()

### Display a random tweet for a given sentiment and a given airline
st.sidebar.subheader("Display a random tweet")
st.sidebar.markdown(selected_subset().sample(n=1)['text'].values[0]) ## This selects a random tweet and displays entry in a first row and column


### Visualize sentiments contained in tweets that customers made
st.sidebar.subheader('Number of tweets by sentiment')
select = st.sidebar.selectbox(label = 'Choose a desired type of plot', options=["Histogram", 'Pie Chart'])

sentiment_count = data['airline_sentiment'].value_counts()
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

if not st.sidebar.checkbox('Hide Vizualization'):
    st.subheader('Number of tweets for a given sentiment ')
    if select == 'Histogram':
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=600)

    elif select == 'Pie Chart':
        fig = px.pie(sentiment_count, values = 'Tweets', names='Sentiment')

    st.plotly_chart(fig)
    st.markdown(" <hr>", unsafe_allow_html=True)


st.sidebar.subheader("When and where are users tweeting from?")
hours = st.sidebar.slider('Hours of a day: ', 0, 24, (0,24), step = 1)
modified_data = data[data['tweet_created'].dt.hour.between(hours[0], hours[1])]
if not st.sidebar.checkbox('Hide Map'):
    st.subheader('Locations of tweets for a given time interval of a day')
    st.markdown(f"{len(modified_data)} tweets were made between {hours[0]}:00 and {hours[1]}:00")
    st.map(modified_data)
    if st.sidebar.checkbox('Show Raw Data'):
        st.dataframe(modified_data)

st.sidebar.subheader("Sentiment comparison across airlines")
airline_choices = st.sidebar.multiselect('Pick airlines you want to compare', options = (data['airline'].unique()))
if len(airline_choices)>0:
    choice_data = options = data[data['airline'].isin(airline_choices)]
    fig_comparison =px.histogram(choice_data, x='airline', y='airline_sentiment',
                                histfunc = 'count', color = 'airline_sentiment',
                                facet_col ='airline_sentiment', labels = {'airline_sentiment':'tweets'})

    st.plotly_chart(fig_comparison)
