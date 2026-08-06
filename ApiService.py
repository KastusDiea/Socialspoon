import requests
import time

from DataService import *

class ApiService:

    def __init__(self):
        self.youtubeAPIKey = None

    def set_yt_api_key(self, key):
        self.youtubeAPIKey = key

    def getRecentVideos(self, platform, creator_name):
        """
        Fetches creator information and latest videos.
        Returns a CreatorData object.
        """

        # Error checks
        if self.youtubeAPIKey is None:
            raise ValueError("YouTube API key is missing")
        if platform is None:
            raise ValueError("Platform cannot be null")
        if creator_name is None:
            raise ValueError("Creator name cannot be null")
        if platform.get_name() != "YouTube":
            raise ValueError("Only YouTube is currently supported")


        # Get channel ID
        channel_id = self.get_channel_id(
            creator_name.get_name()
        )

        if channel_id is None:
            raise Exception("Channel not found")

        # Get subscriber count
        subscribers = self.get_subscriber_count(channel_id)


        # Get videos
        videos = self.get_videos(channel_id)


        # Create CreatorData object
        creator_data = CreatorData(
            name=creator_name.get_name(),
            platform=platform,
            subscribers=subscribers,
            videos=videos
        )


        return creator_data

    def get_channel_id(self, creator_name):

        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={self.youtubeAPIKey}"
            f"&q={creator_name}"
            "&type=channel"
            "&part=id"
        )


        response = requests.get(url).json()
        if "items" not in response or len(response["items"]) == 0:
            return None
        return response["items"][0]["id"]["channelId"]



    def get_subscriber_count(self, channel_id):

        url = (
            "https://www.googleapis.com/youtube/v3/channels"
            f"?key={self.youtubeAPIKey}"
            f"&id={channel_id}"
            "&part=statistics"
        )


        response = requests.get(url).json()


        try:
            return int(
                response["items"][0]
                ["statistics"]
                ["subscriberCount"]
            )

        except Exception:
            return 0



    def get_videos(self, channel_id):
        videos = []

        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?key={self.youtubeAPIKey}"
            f"&channelId={channel_id}"
            "&part=snippet,id"
            "&order=date"
            "&maxResults=10"
        )


        response = requests.get(url).json()


        if "items" not in response:
            raise Exception("YouTube API error")

        for item in response["items"]:


            # Ignore playlists/channels
            if item["id"]["kind"] != "youtube#video":
                continue


            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]


            upload_date = (
                item["snippet"]["publishedAt"]
                .split("T")[0]
            )


            views, likes = self.get_video_stats(video_id)


            video = Video(
                title=title,
                views=views,
                likes=likes,
                upload_date=upload_date
            )


            videos.append(video)
            time.sleep(0.2)

        return videos



    def get_video_stats(self, video_id):

        url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?key={self.youtubeAPIKey}"
            f"&id={video_id}"
            "&part=statistics"
        )


        response = requests.get(url).json()

        try:
            stats = (
                response["items"][0]
                ["statistics"]
            )
            views = int(
                stats.get("viewCount", 0)
            )
            likes = int(
                stats.get("likeCount", 0)
            )


            return views, likes

        except Exception:

            return 0, 0
