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

#import analyzer


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
        st.write("DATE:", dt.fromtimestamp(comment.created_utc))
        st.write("** ", comment.body)
    st.write("Submissions:")
    for sub in user.submissions.new(limit=5):
        st.write("DATE:", dt.fromtimestamp(sub.created_utc))
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
    # for subreddit in subreddit_activity:
    #     comment_words = ''
    #     stopwords = set(STOPWORDS)
    #     for comment in user.comments.new(limit=100):
    #         if comment.subreddit.display_name == subreddit:
    #             # typecaste each val to string
    #             val = str(comment.body)
    #             # split the value
    #             tokens = val.split()
    #             # Converts each token into lowercase
    #             for i in range(len(tokens)):
    #                 tokens[i] = tokens[i].lower()
    #             comment_words += " ".join(tokens) + " "
    #     wordcloud = WordCloud(width = 800, height = 800,
    #                     background_color ='white',
    #                     stopwords = stopwords,
    #                     min_font_size = 10).generate(comment_words)
    #     # plot the WordCloud image
    #     plt.figure(figsize = (8, 8), facecolor = None)
    #     plt.imshow(wordcloud)
    #     plt.axis("off")
    #     st.pyplot()

    # create a bar chart to show the number of comments and submissions by the user
    # comments = [comment.body for comment in user.comments.new(limit=100)]
    # comments_df = pd.DataFrame(comments,columns=['comments'])
    # submissions = [sub.title for sub in user.submissions.new(limit=100)]
    # submissions_df = pd.DataFrame(submissions,columns=['submissions'])
    # activity = pd.concat([comments_df,submissions_df],axis=1)
    # activity.columns = ['comments','submissions']
    # st.bar_chart(activity)

    #create a bar chart to show the number of comments and submissions by the user
    comments = [comment.body for comment in user.comments.new(limit=100)]
    comments_df = pd.DataFrame(comments,columns=['comments'])
    submissions = [sub.title for sub in user.submissions.new(limit=100)]
    submissions_df = pd.DataFrame(submissions,columns=['submissions'])
    # activity = pd.concat([comments_df,submissions_df],axis=1)
    # activity.columns = ['comments','submissions']
    # st.bar_chart(activity)
    # st.write("The above chart shows the number of comments and submissions made by the user")

    #create a pie chart with explode to show the number of comments and submissions by the user
    subreddits = []
    for sub in user.submissions.new(limit=100):
        subreddits.append(sub.subreddit.display_name)
    subreddit_df = pd.DataFrame(subreddits, columns=['subreddit'])
    subreddit_df['count'] = 1
    subreddit_df = subreddit_df.groupby('subreddit').count().reset_index()
    fig = px.treemap(subreddit_df, path=['subreddit'], values='count')
    st.plotly_chart(fig)
    st.write("The above tree map shows the user's most active subreddits")

    # create a histogram to show the user's most common comment lengths
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
    # explode = (0.1, 0)
    # fig1, ax1 = plt.subplots()
    # ax1.pie(activity, explode=explode, labels=labels, autopct='%1.1f%%',
    #         shadow=True, startangle=90)
    # ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    # st.pyplot()
    
    #find the sentiment of the user's comments using pie chart with explode
    analyzer = SentimentIntensityAnalyzer()
    sentiment = []
    for comment in user.comments.new(limit=100):
        sentiment.append(analyzer.polarity_scores(comment.body)['compound'])
    sentiment_df = pd.DataFrame(sentiment, columns=['sentiment'])
    sentiment_df['sentiment'] = sentiment_df['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative')
    sentiment_df['count'] = 1
    sentiment_df = sentiment_df.groupby('sentiment').count().reset_index()
    fig = px.pie(sentiment_df, values='count', names='sentiment', title='Sentiment of User Comments')
    st.plotly_chart(fig)
    st.write("The above pie chart shows the sentiment of the user's comments")

    #find the sentiment of the user's submission using pie chart with explode
    sentiment = []
    for sub in user.submissions.new(limit=100):
        sentiment.append(analyzer.polarity_scores(sub.title)['compound'])
    sentiment_df = pd.DataFrame(sentiment, columns=['sentiment'])
    sentiment_df['sentiment'] = sentiment_df['sentiment'].apply(lambda x: 'positive' if x > 0 else 'negative')
    sentiment_df['count'] = 1
    sentiment_df = sentiment_df.groupby('sentiment').count().reset_index()
    fig = px.pie(sentiment_df, values='count', names='sentiment', title='Sentiment of User Submissions')
    st.plotly_chart(fig)
    st.write("The above pie chart shows the sentiment of the user's submissions")

        


    # create a line chart to show the user's comment karma over time in same graph for the last 5 comments
    comment_karma_over_time = []
    for comment in user.comments.new(limit=5):
        comment_karma_over_time.append((dt.fromtimestamp(comment.created_utc), comment.score))
    karma_df = pd.DataFrame(comment_karma_over_time, columns=['time', 'comment_karma'])
    karma_df['time'] = pd.to_datetime(karma_df['time'])
    karma_df.set_index('time', inplace=True)
    # karma_pivot_df = karma_df.pivot_table(values='comment_karma', columns='time')
    # st.line_chart(karma_pivot_df)
    st.line_chart(karma_df)
    st.write("The above chart shows the user's comment karma over time in same graph for the last 5 comments")

        # comment_karma_over_time = []
    # for comment in user.comments.new(limit=5):
    #     comment_karma_over_time.append((dt.fromtimestamp(comment.created_utc), comment.score))
    #     karma_df = pd.DataFrame(comment_karma_over_time, columns=['time', 'comment_karma'])
    #     karma_df['time'] = pd.to_datetime(karma_df['time'])
    #     karma_df.set_index('time', inplace=True)
    #     st.line_chart(karma_df)

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
    st.write("The above word cloud shows the most common words in the user's comments")

    trophies = user.trophies()
    trophy_names = []
    trophy_descriptions = []
    for trophy in trophies:
        trophy_names.append(trophy)
    trophy_df = pd.DataFrame({'name': trophy_names})
    st.table(trophy_df)
    st.write("The above table shows the trophies earned by the user")
    

    

    # # create a heatmap to show the most active times of the day for the user
    # activity_time = []
    # for comment in user.comments.new(limit=100):
    #     activity_time.append((dt.fromtimestamp(comment.created_utc).hour, dt.fromtimestamp(comment.created_utc).weekday()))
    # activity_df = pd.DataFrame(activity_time, columns=['hour', 'weekday'])
    # activity_pivot = activity_df.pivot_table(values='hour', index='weekday', columns='hour', aggfunc='count')
    # sns.heatmap(activity_pivot,cmap='YlGnBu',annot = True)
    # st.pyplot()
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

    # create a tree map to show the user's most active subreddits
    



