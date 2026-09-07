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
            filter(Title__contains="challenge")
            filter(Title__regex=r"^.*(challenge|vlog).*$")
        """

        df = self._as_df(_db)

        for column, value in kwargs.items():
            if column not in df.columns:
                if df.empty:
                    return df
                if "__contains" in column:
                    base_column = column.replace("__contains", "")
                    if base_column in df.columns:
                        df = df[df[base_column].astype(str).str.contains(value, case=False, na=False)]
                        continue
                if "__regex" in column:
                    base_column = column.replace("__regex", "")
                    if base_column in df.columns:
                        df = df[df[base_column].astype(str).str.contains(value, case=False, na=False, regex=True)]
                        continue
                raise ValueError(f"'{column}' is not in the Database.")

            if isinstance(value, (list, tuple, set, pd.Index)):
                df = df[df[column].isin(value)]
            elif isinstance(value, str):
                values = df[column].astype(str)
                df = df[values.str.contains(value, case=False, na=False, regex=True)]
            else:
                df = df[df[column] == value]

        return df


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

