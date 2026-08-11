from DataService import *
from ApiService import *
from CSVExportService import *
from UiService import *
from DbPullService import *
from DataTransformService import *


def main():

    print("======================================")
    print("     Creator Intelligence System")
    print("======================================\n")

    # ----------------------------
    # Create the platform
    # ----------------------------
    api_key = input("Enter your YouTube API key: ").strip()

    youtube = Platform("YouTube", api_key)

    # ----------------------------
    # Create services
    # ----------------------------
    database = dataService()

    api = ApiService()
    api.set_yt_api_key(api_key)

    exporter = CSVExporter("creator_data.csv")

    # ----------------------------
    # Ask for creator
    # ----------------------------
    creator_input = input("Enter a YouTube creator: ").strip()

    creator = CreatorData(creator_input, youtube.get_name())

    print("\nSearching YouTube...\n")

    try:

        # Retrieve creator data
        creator_data = api.getRecentVideos(
            youtube,
            creator
        )

        # Save to database
        database.createCreatorData(
            creator_data
        )

        print("Creator successfully added.\n")

    except Exception as e:

        print("Error:", e)
        return

    # ----------------------------
    # Display data
    # ----------------------------
    ui = UIService(database.creator_database)
    dTrans = DataTransformService()
    dPull = DbPullService(database.creator_database)

    print("========== DATABASE ==========\n")
    ui.display()

    # ----------------------------
    # Optional filtering
    # ----------------------------
    while True:

        answer = input(
            "\nWould you like to filter the table? (y/n): "
        ).lower()

        if answer == "n":
            break

        column = input(
            "Column (Platform, Creator, Subscribers, Title, Views, Likes, Upload Date): "
        )

        value = input("Value: ")

        try:
            result = dTrans.filter(dPull, **{column: value})
            print(result)

        except Exception as e:
            print(e)

    # ----------------------------
    # Save CSV
    # ----------------------------
    exporter.save_creator_database(
        database.creator_database
    )

    print("\nCSV saved as creator_data.csv")
    print("Program finished.")


if __name__ == "__main__":
    main()
