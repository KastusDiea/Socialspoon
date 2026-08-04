class CreatorData:
    def __init__(self, name, platform, subscribers=0, videos=None):
        self.name = name
        self.platform = platform
        self.subscribers = subscribers
        self.videos = videos if videos else []

    def add_video(self, video):
        self.videos.append(video)

    def get_video_count(self):
        return len(self.videos)




class Platform:
    ALLOWED_PLATFORMS = ["YouTube", "Instagram", "TikTok"]

    def __init__(self, name, api_key):
        if name in self.ALLOWED_PLATFORMS:
            self.platform_name = name
        else:
            raise ValueError("Unsupported platform")

        self.api_key = api_key

    def get_name(self):
        return self.platform_name

    def get_api_key(self):
        return self.api_key


class Video:
    def __init__(self, title, views=0, likes=0, upload_date=""):
        self.title = title
        self.views = views
        self.likes = likes
        self.upload_date = upload_date

    def update_stats(self, views, likes):
        self.views = views
        self.likes = likes


class dataService:
    def __init__(self):
        # Stores CreatorData objects
        self.creator_database = []

    def createCreatorData(self, creator_data):
        if isinstance(creator_data, CreatorData):
            self.creator_database.append(creator_data)
        else:
            raise TypeError("Expected CreatorData object")

    def refreshCreatorData(self, creator_name):
        for creator in self.creator_database:
            if creator.name == creator_name.get_name():
                return creator
        #Make API call

        return None

    def deleteCreatorData(self, creator_name):
        for creator in self.creator_database:
            if creator.name == creator_name.get_name():
                self.creator_database.remove(creator)
                return True

        return False

    def deleteAllData(self):
        self.creator_database.clear()

    def getIntel(self):
        return self.creator_database




if __name__ == "__main__":

    youtube = Platform("YouTube", "API_KEY_123")

    video1 = Video(
        "My First Video",
        views=1000,
        likes=150,
        upload_date="2026-08-01"
    )

    creator = CreatorData(
        "ExampleCreator",
        subscribers=5000,
        videos=[video1]
    )

    service = dataService()
    service.createCreatorData(creator)
    result = service.getIntel()

    for creator in result:
        print("Creator:", creator.name)
        print("Subscribers:", creator.subscribers)
        print("Videos:", creator.get_video_count())

