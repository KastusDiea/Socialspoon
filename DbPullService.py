from CSVExportService import CSVExporter
from DataService import CreatorData
from CreatorTableService import creators_to_dataframe


class DbPullService:
    """Repository for reading persisted creator records from the local CSV database."""

    def __init__(self, csv_path="creator_data.csv", api_service=None, api_key_path="youtube_api_key.txt", api_services=None):
        self.csv_path = csv_path
        self.api_service = api_service
        self.api_services = api_services or {}
        self.api_key_path = api_key_path
        self.api_key = self.load_api_key()
        if self.api_service is not None and self.api_key:
            self.api_service.set_yt_api_key(self.api_key)

    def load_api_key(self):
        try:
            with open(self.api_key_path, encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            return ""

    def save_api_key(self, api_key):
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("API key cannot be empty")
        with open(self.api_key_path, "w", encoding="utf-8") as file:
            file.write(api_key)
        self.api_key = api_key

    def pull_saved_data(self):
        exporter = CSVExporter(filename=self.csv_path)
        return exporter.load_creator_database()

    def save_data(self, creators):
        CSVExporter(filename=self.csv_path).save_creator_database(creators)

    def refresh_data(self, api_service=None):
        """Refresh saved video statistics by creator name and video title."""
        api_service = api_service or self.api_service
        if api_service is None:
            raise ValueError("An API service is required to refresh data")

        creators = self.pull_saved_data()
        try:
            for creator in creators:
                request = CreatorData(creator.name, creator.platform)
                platform_name = creator.platform.get_name()
                refresh_service = self.api_services.get(platform_name, api_service)
                refreshed = refresh_service.getRecentVideos(creator.platform, request)
                videos_by_title = {video.title: video for video in refreshed.videos}

                creator.subscribers = refreshed.subscribers
                for video in creator.videos:
                    latest = videos_by_title.get(video.title)
                    if latest is None:
                        continue
                    video.update_stats(latest.views, latest.likes)
                    video.upload_date = latest.upload_date
        finally:
            self.save_data(creators)
        return creators

    def get_table(self):
        """Return saved records as a DataFrame for legacy callers."""
        return creators_to_dataframe(self.pull_saved_data())

