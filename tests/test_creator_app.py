import tkinter
import unittest
from unittest.mock import patch

import pandas as pd

from CreatorIntelligenceUI import CreatorIntelligence
from DataTransformService import DataTransformService


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

    @patch("CreatorIntelligenceUI.tk.Tk", side_effect=tkinter.TclError("no display"))
    def test_headless_ui_degrades_gracefully(self, _mock_tk):
        creator_db = []
        app = CreatorIntelligence(creator_db)

        self.assertIsNone(app.root)
        app.display([])


if __name__ == "__main__":
    unittest.main()
