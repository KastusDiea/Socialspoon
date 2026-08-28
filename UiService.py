import pandas as pd
from CreatorIntelligenceUI import CreatorIntelligence


class UIService:

    def __init__(self, creator_database):
        self.creator_database = creator_database


    def get_table(self):

        rows = []

        for creator in self.creator_database:

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


    def display(self):
        api_service = None
        table_rows = self.get_table().to_dict(orient="records")
        uic = CreatorIntelligence(table_rows, api_service)
        uic.run()

