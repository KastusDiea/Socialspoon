#Hier kommen die lustigen filter rein afaik
import DbPullService as db
class DataTransformService:

  def filter(self, **kwargs, _db):
        """
        Example:
            filter(Platform="YouTube")
            filter(Creator="MrBeast")
            filter(Subscribers=1000000)
        """

        df = ui.get_table()

        for column, value in kwargs.items():
            if column not in df.columns:
                raise ValueError(f"'{column}' is not in the Database.")

            df = df[df[column] == value]

        return df


    def sort(self, by, ascending=False, _db):
        """
        Example:
            sort("Views")
            sort("Subscribers")
        """

        df = db.get_table()

        if by not in df.columns:
            raise ValueError(f"'{by}' is not possible to sort")

        return df.sort_values(by=by, ascending=ascending)

