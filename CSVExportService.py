import csv


def _parse_int(value):
    if value in (None, ""):
        return 0
    try:
        return int(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0


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

    def load_creator_database(self, filename=None):
        """Load creator data from a CSV and return a list of CreatorData objects.

        Accepts the CSV format produced by `save_creator_database`.
        """
        from DataService import CreatorData, Platform, Video

        path = filename or self.filename
        creators = {}
        try:
            with open(path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    platform_name = row.get("Platform", "")
                    creator_name = row.get("Creator Name") or row.get("Creator") or ""
                    subs = row.get("Subscribers", "")
                    title = row.get("Video Title") or row.get("Title") or ""
                    views = row.get("Views", "")
                    likes = row.get("Likes", "")
                    upload = row.get("Upload Date", "")

                    key = (creator_name, platform_name)
                    if key not in creators:
                        try:
                            plat = Platform(platform_name, "")
                        except ValueError:
                            class _P:
                                def __init__(self, name): self._name = name
                                def get_name(self): return self._name
                            plat = _P(platform_name)

                        creators[key] = CreatorData(
                            creator_name,
                            plat,
                            subscribers=_parse_int(subs),
                            videos=[],
                        )

                    if title:
                        video = Video(
                            title,
                            views=_parse_int(views),
                            likes=_parse_int(likes),
                            upload_date=upload,
                        )
                        creators[key].videos.append(video)
        except FileNotFoundError:
            return []

        return list(creators.values())
