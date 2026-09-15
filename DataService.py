class CreatorData:
    def __init__(self, name, platform, subscribers=0, videos=None):
        self.name = name
        self.platform = platform
        self.subscribers = subscribers
        self.videos = videos or []

    def add_video(self, video):
        self.videos.append(video)

    def get_video_count(self):
        return len(self.videos)
    
    def get_name(self):
        return self.name




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


class DataService:
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


# Preserve the original public name for existing callers.
dataService = DataService

