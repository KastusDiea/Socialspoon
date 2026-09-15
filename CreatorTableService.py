import pandas as pd


TABLE_COLUMNS = [
    "Platform",
    "Creator",
    "Subscribers",
    "Title",
    "Views",
    "Likes",
    "Upload Date",
]


def creator_rows(creators):
    rows = []
    for creator in creators:
        platform = creator.platform.get_name()
        videos = creator.videos or [None]
        for video in videos:
            rows.append(
                {
                    "Platform": platform,
                    "Creator": creator.name,
                    "Subscribers": creator.subscribers,
                    "Title": video.title if video else "",
                    "Views": video.views if video else None,
                    "Likes": video.likes if video else None,
                    "Upload Date": video.upload_date if video else "",
                }
            )
    return rows


def creators_to_dataframe(creators):
    return pd.DataFrame(creator_rows(creators), columns=TABLE_COLUMNS)