

from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns

api_key = 'AIzaSyD84F20SxhA00pVk70rtpgg_PlArM7V8lo'
channel_ids =['UChJW2HOHc5eWZi1X9jf9hTQ',#Hamza Namira
            'UCJCj2HtcnbOyCj1rmKaxwJg',#Mohamed Ramadan
            'UChruvnbwqZ1J1-skg4R5bVQ',#Hassan Shakosh
            'UCBzJgJllSsZunDTD1ekAciA',#Ahmed Saad
            'UC4FPEho0zT1W9gftBydPWIw',#Sherine
            'UC9gXps6xggAzxjjzquNXIaQ',#Wegz
            'UCwTGMDozfRy35__tkvlRc_g',#Mohamed Hamaki
            'UC0PClesNONq7W_h1Mvj1z2g',#Tamer Hosny
            'UCpui0-2JqcAcII4ybpB1q3w'#Amr Diab
            ]

youtube = build('youtube','v3', developerKey=api_key)

"""### Comparing The Channel Statistics"""

# Function to get the channel statistics
def get_channel_stats(youtube, channel_ids):
    all_data=[]
    request = youtube.channels().list(
                part='snippet,contentDetails,statistics',id=','.join(channel_ids))
    response = request.execute()

    for i in range(len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscriber = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_videos = response['items'][i]['statistics']['videoCount'],
                    Playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        all_data.append(data)

    return all_data

#print the channel_stats
get_channel_stats(youtube, channel_ids)

# Save the output in the varibale
channel_stats = get_channel_stats(youtube, channel_ids)

# Convert it into PandasDataframe
channel_data = pd.DataFrame(channel_stats)

# See the data in rows and columns format
channel_data

# Check the column types
channel_data.dtypes

# Change the data types
channel_data['Subscriber'] = pd.to_numeric(channel_data['Subscriber'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])

# Re-check data types after changing data types
channel_data.dtypes

# Create an barplot to easily compare the subscriber count
sns.set_theme(rc={'figure.figsize':(20,5)})

ax = sns.barplot(x='Channel_name',y='Subscriber',data=channel_data)

"""From the above chart we can see that, **Mohamed Ramadan** has the maximum number of subscribers compre to the other channels."""

# Create an barplot to easily compare the video count
ax = sns.barplot(x='Channel_name',y='Total_videos',data=channel_data)

"""From the above chart we can see that, Mohamed Ramadan had uploaded maximum number of videos compare to the other youtubers.

Now we will do further analysis of 'Mohamed Ramadan' channel by analyzing it's all videos data.
"""



"""### Analysis Of 'Mohamed Ramadan' Channel

Now we will build a logic to extract video details from **'Mohamed Ramadan'**. We shall extract details such as video title, total views each video has got, total number of likes, and comments each video has got. We will then analyze this data by loading it into a pandas dataframe. At the end we will create some simple visualization using Seaborn python library.
"""

# Extracting playlist_id for 'Mohamed Ramadan' channel
playlist_id = channel_data.loc[channel_data['Channel_name']=='Mohamed Ramadan I محمد رمضان','Playlist_id'].iloc[0]

# Print the playlist_id
playlist_id

# Function to get the video statistics for 'Mohamed Ramadan' channel

def get_video_ids(youtube, playlist_id):

    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50,
                pageToken = next_page_token)

            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
                next_page_token = response.get('nextPageToken')

    return video_ids

# storing the output in the variable
video_ids = get_video_ids(youtube, playlist_id)

# See the total Videos uploaded by Alex
len(video_ids)

# Function to extract some stats for each video
def get_video_details(youtube, video_ids):
    all_video_stats = []
    total_video_ids = len(video_ids)

    for i in range(0, total_video_ids, 50):
        batch_ids = video_ids[i:i+50]
        print(f"Processing batch {i // 50 + 1} with {len(batch_ids)} video IDs.")

        try:
            request = youtube.videos().list(
                part='snippet,statistics',
                id=','.join(batch_ids)
            )
            response = request.execute()

            # Print the response to debug
            print(response)

            if 'items' in response:
                for video in response['items']:
                    video_stats = {
                        'Title': video['snippet'].get('title', 'N/A'),
                        'Published_date': video['snippet'].get('publishedAt', 'N/A'),
                        'Views': video['statistics'].get('viewCount', 'N/A'),
                        'Likes': video['statistics'].get('likeCount', 'N/A'),
                        'Comments': video['statistics'].get('commentCount', 'N/A')
                    }
                    all_video_stats.append(video_stats)
            else:
                print("No items found in response.")

        except Exception as e:
            print(f"An error occurred: {e}")

    # Check if all video IDs were processed
    print(f"Total video IDs: {total_video_ids}")
    print(f"Total video details fetched: {len(all_video_stats)}")

    return all_video_stats

# store the video stats in the variable
video_details = get_video_details(youtube, video_ids)

# store the video data in the DataFrame format
video_data = pd.DataFrame(video_details)

# See the top 5 rows
video_data

# See the data types of columns
video_data.dtypes

video_data['Comments'] = video_data['Comments'].replace("N/A",0)
video_data['Likes'] = video_data['Likes'].replace("N/A",0)

# Change the data types
video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Comments'] = pd.to_numeric(video_data['Comments'])

# Again see the data
video_data.head()

# Re-check the data types
video_data.dtypes

# Extract top 10 videos by views
top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)

# See the top 10 video details
top10_videos

# Created an barplot to visually compare Top videos
ax1 = sns.barplot(x='Views',y='Title', data=top10_videos)

"""The 'SQL' related videos uploaded by Mohamed Ramadan  got the maximum number of views."""

# Extract Month and Year From Date
video_data['Published_Month'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%b')
video_data['Published_Year'] = pd.to_datetime(video_data['Published_date']).dt.strftime('%Y')

# See the data
video_data.head()

# See the data types
video_data.dtypes

# Get the year wise video count
videos_per_year = video_data.groupby('Published_Year',as_index=False).size()

videos_per_year

# Plot the barplot to easily compare the yearly uploaded video count
ax2 = sns.barplot(x='Published_Year',y='size',data=videos_per_year)

# Get the month wise video count
videos_per_month = video_data.groupby('Published_Month',as_index=False).size()

videos_per_month

sort_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

videos_per_month.index = pd.CategoricalIndex(videos_per_month['Published_Month'],categories=sort_order,ordered=True)

videos_per_month.sort_index()

# Plot the barplot to easily compare the monthly uploaded video count
ax3 = sns.barplot(x='Published_Month',y='size',data=videos_per_month.sort_index())

