from CSVExportService import CSVExporter


class DbPullService:
    """Repository for reading persisted creator records from the local CSV database."""

    def __init__(self, csv_path="creator_data.csv"):
        self.csv_path = csv_path

    def pull_saved_data(self):
        exporter = CSVExporter(filename=self.csv_path)
        return exporter.load_creator_database()

    def get_table(self):
        """Backward-compatible convenience method for callers that still expect a DataFrame.

        Note: table conversion is presentation logic and should live outside the persistence layer.
        """
        import pandas as pd

        rows = []
        for creator in self.pull_saved_data():
            platform = creator.platform.get_name()

            if len(creator.videos) == 0:
                rows.append({
                    "Platform": platform,
                    "Creator": creator.name,
                    "Subscribers": creator.subscribers,
                    "Title": "",
                    "Views": None,
                    "Likes": None,
                    "Upload Date": ""
                })
            else:
                for video in creator.videos:
                    rows.append({
                        "Platform": platform,
                        "Creator": creator.name,
                        "Subscribers": creator.subscribers,
                        "Title": video.title,
                        "Views": video.views,
                        "Likes": video.likes,
                        "Upload Date": video.upload_date
                    })

        return pd.DataFrame(rows)

