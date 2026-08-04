import csv


class CSVExporter:

    def __init__(self, filename="creator_data.csv"):
        self.filename = filename


    def save_creator_database(self, creator_database):

        with open(self.filename, mode="w", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            writer.writerow([
                "Platform",
                "Creator Name",
                "Subscribers",
                "Video Title",
                "Views",
                "Likes",
                "Upload Date"
            ])

            for creator in creator_database:

                platform_name = creator.platform.get_name()

                if len(creator.videos) == 0:
                    writer.writerow([
                        platform_name,
                        creator.name,
                        creator.subscribers,
                        "",
                        "",
                        "",
                        ""
                    ])

                else:
                    for video in creator.videos:
                        writer.writerow([
                            platform_name,
                            creator.name,
                            creator.subscribers,
                            video.title,
                            video.views,
                            video.likes,
                            video.upload_date
                        ])

        print(f"Saved creator data to {self.filename}")
