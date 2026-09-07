import tkinter
import unittest
from unittest.mock import patch

import pandas as pd

from CreatorIntelligenceUI import CreatorIntelligence
from DataService import CreatorData, Video, Platform
from DataTransformService import DataTransformService
from DbPullService import DbPullService


class TestCreatorApp(unittest.TestCase):
    def test_filter_accepts_multiple_platforms(self):
        df = pd.DataFrame(
            [
                {"Platform": "YouTube", "Creator": "A", "Subscribers": 10, "Title": "T1"},
                {"Platform": "Instagram", "Creator": "B", "Subscribers": 20, "Title": "T2"},
                {"Platform": "TikTok", "Creator": "C", "Subscribers": 30, "Title": "T3"},
            ]
        )

        result = DataTransformService().filter(df, Platform=["YouTube", "Instagram"])

        self.assertEqual(set(result["Platform"]), {"YouTube", "Instagram"})
        self.assertEqual(len(result), 2)

    def test_db_pull_service_reads_saved_creator_csv(self):
        with open("tmp_creator_data.csv", "w", encoding="utf-8", newline="") as fh:
            fh.write(
                "Platform,Creator Name,Subscribers,Video Title,Views,Likes,Upload Date\n"
                "YouTube,TestCreator,12345,Sample Video,500,50,2026-09-01\n"
            )

        service = DbPullService("tmp_creator_data.csv")
        creators = service.pull_saved_data()

        self.assertEqual(len(creators), 1)
        self.assertEqual(creators[0].name, "TestCreator")
        self.assertEqual(creators[0].videos[0].title, "Sample Video")

        import os
        os.remove("tmp_creator_data.csv")

    @patch("CreatorIntelligenceUI.tk.Tk", side_effect=tkinter.TclError("no display"))
    def test_headless_ui_degrades_gracefully(self, _mock_tk):
        creator_db = []
        app = CreatorIntelligence(creator_db)

        self.assertIsNone(app.root)
        app.display([])

    def test_ui_load_creator_fetches_and_stores_data(self):
        class FakeAPI:
            def __init__(self):
                self.key = None

            def set_yt_api_key(self, key):
                self.key = key

            def getRecentVideos(self, platform, creator):
                self.asserted = (platform.get_name(), creator.get_name())
                return CreatorData(creator.get_name(), platform, subscribers=999, videos=[Video("Sample", 100, 10, "2026-09-01")])

        creator_db = []
        app = CreatorIntelligence(creator_db, api_service=FakeAPI())
        app.root = None
        app.status = None
        app.table = None
        app.records = []

        app.api_key.set("abc123")
        app.creator_name.set("DemoCreator")

        app.load_creator_data()

        self.assertEqual(len(creator_db), 1)
        self.assertEqual(creator_db[0].name, "DemoCreator")
        self.assertEqual(creator_db[0].videos[0].title, "Sample")


if __name__ == "__main__":
    unittest.main()
