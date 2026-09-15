from ApiService import ApiService
from CSVExportService import CSVExporter
from DataService import DataService
from DbPullService import DbPullService
from UiService import UIService


def main():

    print("======================================")
    print("     Creator Intelligence System")
    print("======================================\n")

    database = DataService()
    api = ApiService()
    exporter = CSVExporter("creator_data.csv")

    # If a local CSV exists, load it into the in-memory database first
    db_pull = DbPullService("creator_data.csv")
    existing = db_pull.pull_saved_data()
    if existing:
        for c in existing:
            try:
                database.createCreatorData(c)
            except TypeError:
                database.creator_database.append(c)

    print("\nSearching YouTube...\n")
    ui = UIService(database.creator_database)

    print("========== DATABASE ==========\n")
    ui.display(api)



if __name__ == "__main__":
    main()
