import praw
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime as dt
from wordcloud import WordCloud

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

# create the streamlit app
st.title("Reddit User Analysis")

# get the username from the user
username = st.text_input("Enter a Reddit username:")

# def print_user_info(user):
#     print("Username: ",user.name) 
#     print("Comment karma: ",user.comment_karma)
#     print("Link karma: ",user.link_karma)
#     print("Account created at: ",user.created_utc)
#     print("Is employee: ",user.is_employee)
#     print("Has Reddit Gold: ",user.is_gold)
#     print("Is moderator: ",user.is_mod)
#     print("Comments:")
#     for comment in user.comments.new(limit=5):
#         print("DATE:",dt.datetime.fromtimestamp(comment.created_utc))
#         print("** ",comment.body)
#     print("Submissions:")
#     for sub in user.submissions.new(limit=5):
#         print("DATE:",dt.datetime.fromtimestamp(sub.created_utc))
#         print("** ",sub.title)
#     print("Trophies: ",user.trophies())

def print_user_info(user):
    data = [["Username", user.name],
    ["Comment karma", user.comment_karma],
    ["Link karma", user.link_karma],
    ["Account created at", user.created_utc],
    ["Is employee", user.is_employee],
    ["Has Reddit Gold", user.is_gold],
    ["Is moderator", user.is_mod],
    ["Trophies", user.trophies()]]
    table = st.table(data)
    st.write("Comments:")
    for comment in user.comments.new(limit=5):
        st.write("DATE:", dt.datetime.fromtimestamp(comment.created_utc))
        st.write("** ", comment.body)
    st.write("Submissions:")
    for sub in user.submissions.new(limit=5):
        st.write("DATE:", dt.datetime.fromtimestamp(sub.created_utc))
        st.write("** ",sub.title)

# if the user has entered a username, display the user data
if username:
    user = get_user_data(username)
    print_user_info(user)

    subreddit_activity = {}
    for comment in user.comments.new(limit=100):
        if comment.subreddit.display_name in subreddit_activity:
            subreddit_activity[comment.subreddit.display_name] += 1
        else:
            subreddit_activity[comment.subreddit.display_name] = 1
    st.bar_chart(pd.DataFrame.from_dict(subreddit_activity, orient='index', columns=['comments']))
    st.text("The above chart shows the number of comments made by the user in each subreddit")
    # create a wordcloud of the user's comments in each subreddit
    for subreddit in subreddit_activity:
        subreddit_comments = []
        for comment in user.comments.new(limit=100):
            if comment.subreddit.display_name == subreddit:
                subreddit_comments.append(comment.body)
        wordcloud = WordCloud(width=800, height=400, max_words=100).generate(" ".join(subreddit_comments))
        st.image(wordcloud, caption=f'Wordcloud of comments in {subreddit}', use_column_width=True)

    # create a bar chart to show the number of comments and submissions by the user
    comments = [comment.body for comment in user.comments.new(limit=100)]
    comments_df = pd.DataFrame(comments,columns=['comments'])
    submissions = [sub.title for sub in user.submissions.new(limit=100)]
    submissions_df = pd.DataFrame(submissions,columns=['submissions'])
    activity = pd.concat([comments_df,submissions_df],axis=1)
    activity.columns = ['comments','submissions']
    st.bar_chart(activity)

    # create a line chart to show the user's comment karma over time
    comment_karma_over_time = []
    for comment in user.comments.new(limit=100):
        comment_karma_over_time.append((dt.fromtimestamp(comment.created_utc), comment.score))
        karma_df = pd.DataFrame(comment_karma_over_time, columns=['time', 'comment_karma'])
        karma_df['time'] = pd.to_datetime(karma_df['time'])
        karma_df.set_index('time', inplace=True)
        st.line_chart(karma_df)

    # create a word cloud to show the most common words in the user's comments
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
    wordcloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10).generate(comment_words)
    # plot the WordCloud image
    plt.figure(figsize = (8, 8), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad = 0)
    st.pyplot()

    # create a pie chart to show the user's trophies
    trophies = user.trophies()
    trophy_names = []
    trophy_descriptions = []
    for trophy in trophies:
        trophy_names.append(trophy['name'])
        trophy_descriptions.append(trophy['description'])
    trophy_df = pd.DataFrame({'name': trophy_names, 'description': trophy_descriptions})
    fig = px.pie(trophy_df, values='description', names='name')
    st.plotly_chart(fig)

    # create a heatmap to show the most active times of the day for the user
    activity_time = []
    for comment in user.comments.new(limit=100):
        activity_time.append((dt.fromtimestamp(comment.created_utc).hour, dt.fromtimestamp(comment.created_utc).weekday()))
    activity_df = pd.DataFrame(activity_time, columns=['hour', 'weekday'])
    activity_pivot = activity_df.pivot_table(values='hour', index='weekday', columns='hour', aggfunc='count')
    sns.heatmap(activity_pivot,cmap='YlGnBu',annot = True)
    st.pyplot()

    # create a tree map to show the user's most active subreddits
    subreddits = []
    for sub in user.submissions.new(limit=100):
        subreddits.append(sub.subreddit.display_name)
    subreddit_df = pd.DataFrame(subreddits, columns=['subreddit'])
    subreddit_df['count'] = 1
    subreddit_df = subreddit_df.groupby('subreddit').count().reset_index()
    fig = px.treemap(subreddit_df, path=['subreddit'], values='count')
    st.plotly_chart(fig)

    # create a histogram to show the user's most common comment lengths
    comment_lengths = []
    for comment in user.comments.new(limit=100):
        comment_lengths.append(len(comment.body))
    comment_lengths_df = pd.DataFrame(comment_lengths, columns=['length'])
    fig = px.histogram(comment_lengths_df, x='length')
    st.plotly_chart(fig)



