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
    #api_key = input("Enter your YouTube API key: ").strip()

    #youtube = Platform("YouTube", api_key)

    # ----------------------------
    # Create services
    # ----------------------------
    database = dataService()
    api = ApiService()
    exporter = CSVExporter("creator_data.csv")

    # If a local CSV exists, load it into the in-memory database first
    existing = exporter.load_creator_database()
    if existing:
        for c in existing:
            try:
                database.createCreatorData(c)
            except Exception:
                # fallback: append directly
                database.creator_database.append(c)

    # ----------------------------
    # Ask for creator
    # ----------------------------
    #creator_input = input("Enter a YouTube creator: ").strip()

    #creator = CreatorData(creator_input, youtube.get_name())

    print("\nSearching YouTube...\n")

    #try:

        # Retrieve creator data
        #creator_data = api.getRecentVideos(
            #youtube,
            #creator
        #)

        # Save to database
       # database.createCreatorData(
            #creator_data
        #)

        #print("Creator successfully added.\n")

    #except Exception as e:

        #print("Error:", e)
        #return

    # ----------------------------
    # Display data
    # ----------------------------
    ui = UIService(database.creator_database)
    dTrans = DataTransformService()
    dPull = DbPullService(database.creator_database)

    print("========== DATABASE ==========\n")
    ui.display(api)



if __name__ == "__main__":
    main()
