#Hier kommen die lustigen filter rein afaik
public class DataTransformService()
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
