import praw
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime as dt
from wordcloud import WordCloud, STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from PIL import Image


#set streamlit warning to false
st.set_option('deprecation.showfileUploaderEncoding', False)

#set all streamlit warnig to false
st.set_option('deprecation.showPyplotGlobalUse', False)



# initialize the reddit instance
reddit = praw.Reddit(client_id='w0cDom4nIf5druip4y9zSw', \
                     client_secret='mtCul8hEucwNky7hLwgkewlLPzH0sg', \
                     user_agent='Profile extractor', \
                     username='CarelessSwordfish541', \
                     password='Testing@2022')

# create a function to get user data
def get_user_data(username):
    user = reddit.redditor(username)
    return user

#change background color to black
# st.markdown('<link rel="stylesheet" type="text/css" href="custom.css">', unsafe_allow_html=True)

# create the streamlit app
st.title("Reddit User Analysis 👀")

st.write("Keep scrolling....")

# create a background image
# image = Image.open('reddit.jpg')
# Get the image from the GitHub repository
img_url = "https://github.com/Lagstill/Social_media/blob/main/Reddit/reddit.jpg"
response = requests.get(img_url)

# Open the image using PIL
image = Image.open(requests.get(img_url, stream=True).raw)

st.image(image, use_column_width=True ,caption='Reddit is a social news aggregation, web content rating, and discussion website. Registered members submit content to the site such as links, text posts, and images, which are then voted up or down by other members. Content entries are organized by areas of interest called "subreddits".', width=800)

# create a sidebar
st.sidebar.title("Reddit users, so unique and rare (❁´◡`❁),\nBut data analysis shows they all share UwU,\nThe same interests, habits, and views o(^▽^)o,\nNo surprise, on the internet, everyone's news.")

# create a sidebar subheader
st.sidebar.subheader("Step right up, folks! Enter your Reddit username and let's see what kind of internet shenanigans you've been up to! But don't worry, we won't tell your mom... unless she's on Reddit too.")

# create a sidebar text input
username = st.sidebar.text_input("Let's see what you're all about...or not, who am I kidding, down here boss")


def print_user_info(user):

    data = [["Username", user.name],
    ["Comment karma", user.comment_karma],
    ["Link karma", user.link_karma],
    ["Account created at", user.created_utc],
    ["Is employee", user.is_employee],
    ["Has Reddit Gold", user.is_gold],
    ["Is moderator", user.is_mod],
    ["Trophies", user.trophies()]]
    columns = ["Attribute", "value"]
    df = pd.DataFrame(data, columns=columns)
    st.table(df)

    
if username:
    user = get_user_data(username)
    try:
        user.comment_karma
        st.write(f'Username "{user}" is available!')
    except:
        st.write(f'Username "{user}" is not available. Here are some suggestions:')
        default_usernames = ['ShittyMorph','moojo','Arinupa', 'JigZawP', 'Andromeda321','NeuroticNurse']
        for name in default_usernames:
            st.write("-->",name)
        st.stop()

    #display user's icon
    st.image(user.icon_img)

 
    subreddits = []
    for sub in user.submissions.new(limit=100):
        subreddits.append(sub.subreddit.display_name)
    subreddit_df = pd.DataFrame(subreddits, columns=['subreddit'])
    subreddit_df['count'] = 1
    subreddit_df = subreddit_df.groupby('subreddit').count().reset_index()
    fig = px.treemap(subreddit_df, path=['subreddit'], values='count')
    st.plotly_chart(fig)
    st.write("The above tree map shows the user's most active subreddits")

    if st.checkbox("User's portfolio"):
        print_user_info(user)

    if st.checkbox("User's activity"):
        subreddit_activity = {}
        for comment in user.comments.new(limit=100):
            if comment.subreddit.display_name in subreddit_activity:
                subreddit_activity[comment.subreddit.display_name] += 1
            else:
                subreddit_activity[comment.subreddit.display_name] = 1
        st.bar_chart(pd.DataFrame.from_dict(subreddit_activity, orient='index', columns=['comments']))
        st.text("The above chart shows the number of comments made by the user in each subreddit")

        trophies = user.trophies()
        trophy_names = []
        trophy_descriptions = []
        for trophy in trophies:
            trophy_names.append(trophy)
        trophy_df = pd.DataFrame({'name': trophy_names})
        st.table(trophy_df)
        st.write("The above table shows the trophies earned by the user")

    #create a bar chart to show the number of comments and submissions by the user
    comments = [comment.body for comment in user.comments.new(limit=100)]
    comments_df = pd.DataFrame(comments,columns=['comments'])
    submissions = [sub.title for sub in user.submissions.new(limit=100)]
    submissions_df = pd.DataFrame(submissions,columns=['submissions'])

    # create a word cloud to show the most common words in the user's comments
    try:
        comment_words = ''
        stopwords = set(STOPWORDS)
        for val in comments_df['comments']:
            # typecaste each val to string
            val = str(val)
            # split the value
            tokens = val.split()
            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()
            comment_words += " ".join(tokens) + " "
        wordcloud = WordCloud(width = 500, height = 500,
                        background_color ='black',
                        stopwords = stopwords,
                        min_font_size = 10).generate(comment_words)
        # plot the WordCloud image
        plt.figure(figsize = (8, 8), facecolor = None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.tight_layout(pad = 0)
        st.pyplot()
        st.write("The above word cloud shows the most common words in the user's comments")
    except:
        st.write("The user has no comments")

    # create a histogram to show the user's most common comment lengths
    if st.checkbox('Most common comment lengths'):
        comment_lengths = []
        for comment in user.comments.new(limit=100):
            comment_lengths.append(len(comment.body))
        comment_lengths_df = pd.DataFrame(comment_lengths, columns=['length'])
        fig = px.histogram(comment_lengths_df, x='length')
        st.plotly_chart(fig)
        st.write("The above histogram shows the user's most common comment lengths")

    comments = [comment.body for comment in user.comments.new(limit=100)]
    submissions = [sub.title for sub in user.submissions.new(limit=100)]
    activity = [len(comments),len(submissions)]
    labels = ['Comments','Submissions']

    # create a line chart to show the user's comment karma over time in same graph for the last 5 comments
    if st.checkbox("User's comment karma over time"):
        comment_karma_over_time = []
        for comment in user.comments.new(limit=50):
            comment_karma_over_time.append((dt.fromtimestamp(comment.created_utc), comment.score))
        karma_df = pd.DataFrame(comment_karma_over_time, columns=['time', 'comment_karma'])
        karma_df['time'] = pd.to_datetime(karma_df['time'])
        karma_df.set_index('time', inplace=True)

        st.line_chart(karma_df)
        st.write("The above chart shows the user's comment karma over time in same graph for the last 50 comments")

    analyzer = SentimentIntensityAnalyzer()

    # Sentiment of user comments
    sentiment = []
    for comment in user.comments.new(limit=100):
        sentiment.append(analyzer.polarity_scores(comment.body)['compound'])
    sentiment_df = pd.DataFrame(sentiment, columns=['sentiment'])
    sentiment_df['sentiment'] = sentiment_df['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative')
    sentiment_df['count'] = 1
    sentiment_df = sentiment_df.groupby('sentiment').count().reset_index()
    fig_comment = px.pie(sentiment_df, values='count', names='sentiment', title='Sentiment of User Comments')
    st.plotly_chart(fig_comment)
    st.write("The above pie chart shows the sentiment of the user's comments")

    # Sentiment of user submissions
    sentiment = []
    for sub in user.submissions.new(limit=100):
        sentiment.append(analyzer.polarity_scores(sub.title)['compound'])
    sentiment_df = pd.DataFrame(sentiment, columns=['sentiment'])
    sentiment_df['sentiment'] = sentiment_df['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative')
    sentiment_df['count'] = 1
    sentiment_df = sentiment_df.groupby('sentiment').count().reset_index()
    fig_submission = px.pie(sentiment_df, values='count', names='sentiment', title='Sentiment of User Submissions')
    st.plotly_chart(fig_submission)
    st.write("The above pie chart shows the sentiment of the user's submissions")

    comments_limit = st.number_input("Enter number of comments to view:", min_value=1, max_value=100, value=3)
    submissions_limit = st.number_input("Enter number of submissions to view:", min_value=1, max_value=100, value=3)

    st.write("Comments:")
    data = []
    for comment in user.comments.new(limit=comments_limit):
        data.append([dt.fromtimestamp(comment.created_utc), comment.body])
    columns = ['Time', 'Comment']
    df = pd.DataFrame(data, columns=columns)
    st.table(df)

    st.write("Submissions:")
    data = []
    for sub in user.submissions.new(limit=submissions_limit):
        data.append([dt.fromtimestamp(sub.created_utc), sub.title])
    columns = ["Time", "Submission"]
    df = pd.DataFrame(data, columns=columns)
    st.table(df)

    
    activity_time = []
    for comment in user.comments.new(limit=100):
        activity_time.append((dt.fromtimestamp(comment.created_utc).hour, dt.fromtimestamp(comment.created_utc).weekday()))
    activity_df = pd.DataFrame(activity_time, columns=['hour', 'weekday'])
    if activity_df.shape[0] == 0:
        st.error("No activity data found")
    else:
        # Adding a new column in the activity_df for counting the number of occurances of hour and day
        activity_df['count'] = 1
        activity_pivot = activity_df.pivot_table(values='count', index='weekday', columns='hour', aggfunc='sum')
        sns.heatmap(activity_pivot, cmap='YlGnBu', annot=True)
        st.pyplot()

    



