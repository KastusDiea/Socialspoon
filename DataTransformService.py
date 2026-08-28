#Hier kommen die lustigen filter rein afaik
import DbPullService as db
import pandas as pd

class DataTransformService:

    def _as_df(self, src):
        if hasattr(src, 'get_table'):
            return src.get_table()
        if isinstance(src, pd.DataFrame):
            return src
        raise TypeError('DataTransformService expects a DataFrame or an object with get_table()')

    def filter(self, _db, **kwargs):
        """
        Example:
            filter(Platform="YouTube")
            filter(Creator="MrBeast")
            filter(Subscribers=1000000)
        """

        df = self._as_df(_db)

        for column, value in kwargs.items():
            if column not in df.columns:
                raise ValueError(f"'{column}' is not in the Database.")

            df = df[df[column] == value]

        return df

# TODO: add contains/regex filtering support so keyword searches work (e.g. title contains)


    def sort(self, _db, by, ascending=False):
        """
        Example:
            sort("Views")
            sort("Subscribers")
        """

        df = self._as_df(_db)

        if by not in df.columns:
            raise ValueError(f"'{by}' is not possible to sort")

        return df.sort_values(by=by, ascending=ascending)

