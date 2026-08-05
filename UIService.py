import pandas as pd


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
        """
        Prints the entire table.
        """
        print(self.get_table())


    def filter(self, **kwargs):
        """
        Example:
            filter(Platform="YouTube")
            filter(Creator="MrBeast")
            filter(Subscribers=1000000)
        """

        df = self.get_table()

        for column, value in kwargs.items():
            if column not in df.columns:
                raise ValueError(f"'{column}' is not in the Database.")

            df = df[df[column] == value]

        return df


    def sort(self, by, ascending=False):
        """
        Example:
            sort("Views")
            sort("Subscribers")
        """

        df = self.get_table()

        if by not in df.columns:
            raise ValueError(f"'{by}' is not possible to sort")

        return df.sort_values(by=by, ascending=ascending)
