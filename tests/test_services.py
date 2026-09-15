import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from ApiService import ApiService
from CSVExportService import CSVExporter
from CreatorTableService import creators_to_dataframe
from DataService import CreatorData, DataService, Platform, Video
from DataTransformService import DataTransformService
from DbPullService import DbPullService
from instagram_api import InstagramApiService


class TestDataService(unittest.TestCase):
    def setUp(self):
        self.platform = Platform("YouTube", "key")
        self.creator = CreatorData("Creator", self.platform)
        self.service = DataService()

    def test_create_delete_and_find_creator(self):
        self.service.createCreatorData(self.creator)

        self.assertIs(self.service.refreshCreatorData(self.creator), self.creator)
        self.assertTrue(self.service.deleteCreatorData(self.creator))
        self.assertFalse(self.service.deleteCreatorData(self.creator))

    def test_create_rejects_non_creator_data(self):
        with self.assertRaises(TypeError):
            self.service.createCreatorData(object())


class TestCreatorTableService(unittest.TestCase):
    def test_creators_without_videos_keep_a_single_placeholder_row(self):
        creator = CreatorData("Creator", Platform("TikTok", "key"), subscribers=7)

        table = creators_to_dataframe([creator])

        self.assertEqual(list(table.columns), [
            "Platform", "Creator", "Subscribers", "Title", "Views",
            "Likes", "Upload Date",
        ])
        self.assertEqual(len(table), 1)
        self.assertEqual(table.iloc[0]["Creator"], "Creator")
        self.assertEqual(table.iloc[0]["Title"], "")


class TestCSVExporter(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        creator = CreatorData(
            "Creator",
            Platform("YouTube", "key"),
            subscribers=1200,
            videos=[Video("Video", views=300, likes=20, upload_date="2026-09-01")],
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.csv"
            exporter = CSVExporter(path)
            exporter.save_creator_database([creator])

            loaded = exporter.load_creator_database()

        self.assertEqual(loaded[0].subscribers, 1200)
        self.assertEqual(loaded[0].videos[0].views, 300)
        self.assertEqual(loaded[0].videos[0].likes, 20)

    def test_load_invalid_numeric_values_as_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.csv"
            path.write_text(
                "Platform,Creator Name,Subscribers,Video Title,Views,Likes,Upload Date\n"
                "YouTube,Creator,not-a-number,Video,unknown,,2026-09-01\n",
                encoding="utf-8",
            )

            loaded = CSVExporter(path).load_creator_database()

        self.assertEqual(loaded[0].subscribers, 0)
        self.assertEqual(loaded[0].videos[0].views, 0)
        self.assertEqual(loaded[0].videos[0].likes, 0)

    def test_refresh_data_updates_matching_video_and_preserves_unknown_video(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.csv"
            original = CreatorData(
                "Creator",
                Platform("YouTube", "key"),
                subscribers=100,
                videos=[
                    Video("Known", views=1, likes=2, upload_date="old"),
                    Video("Not returned", views=3, likes=4, upload_date="old"),
                ],
            )
            exporter = CSVExporter(path)
            exporter.save_creator_database([original])

            refreshed_creator = CreatorData(
                "Creator",
                original.platform,
                subscribers=200,
                videos=[Video("Known", views=10, likes=20, upload_date="new")],
            )
            api = Mock()
            api.getRecentVideos.return_value = refreshed_creator

            result = DbPullService(path, api_service=api).refresh_data()

            saved = exporter.load_creator_database()

        self.assertEqual(result[0].subscribers, 200)
        self.assertEqual(result[0].videos[0].views, 10)
        self.assertEqual(result[0].videos[0].likes, 20)
        self.assertEqual(result[0].videos[1].views, 3)
        self.assertEqual(saved[0].videos[0].upload_date, "new")
        api.getRecentVideos.assert_called_once()


class TestDbPullService(unittest.TestCase):
    def test_api_key_is_saved_and_loaded_into_api_service(self):
        api = Mock()
        with tempfile.TemporaryDirectory() as directory:
            key_path = Path(directory) / "youtube_api_key.txt"
            service = DbPullService(api_service=api, api_key_path=key_path)
            service.save_api_key("  saved-key  ")

            restarted_api = Mock()
            restarted = DbPullService(api_service=restarted_api, api_key_path=key_path)

            self.assertEqual(service.load_api_key(), "saved-key")
            self.assertEqual(restarted.api_key, "saved-key")
            restarted_api.set_yt_api_key.assert_called_once_with("saved-key")

    def test_refresh_uses_service_for_creator_platform(self):
        youtube_api = Mock()
        instagram_api = Mock()
        instagram_api.getRecentVideos.return_value = CreatorData(
            "Creator",
            Platform("Instagram", ""),
            subscribers=9,
            videos=[],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.csv"
            CSVExporter(path).save_creator_database([
                CreatorData("Creator", Platform("Instagram", ""), subscribers=1)
            ])

            DbPullService(
                path,
                api_service=youtube_api,
                api_services={"Instagram": instagram_api},
            ).refresh_data()

        instagram_api.getRecentVideos.assert_called_once()
        youtube_api.getRecentVideos.assert_not_called()

    def test_refresh_saves_partial_data_when_a_creator_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "creators.csv"
            creators = [
                CreatorData("First", Platform("YouTube", "key"), subscribers=1),
                CreatorData("Second", Platform("YouTube", "key"), subscribers=2),
            ]
            exporter = CSVExporter(path)
            exporter.save_creator_database(creators)
            api = Mock()
            api.getRecentVideos.side_effect = [
                CreatorData("First", creators[0].platform, subscribers=10),
                RuntimeError("temporary failure"),
            ]

            with self.assertRaises(RuntimeError):
                DbPullService(path, api_service=api).refresh_data()

            saved = exporter.load_creator_database()

        self.assertEqual(saved[0].subscribers, 10)
        self.assertEqual(saved[1].subscribers, 2)


class TestDataTransformService(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame([
            {"Creator": "Alpha", "Views": 10, "Platform": "YouTube"},
            {"Creator": "Beta", "Views": 30, "Platform": "TikTok"},
        ])
        self.service = DataTransformService()

    def test_contains_filter_and_sort(self):
        filtered = self.service.filter(self.data, Creator__contains="alp")
        sorted_data = self.service.sort(self.data, by="Views")

        self.assertEqual(filtered.iloc[0]["Creator"], "Alpha")
        self.assertEqual(list(sorted_data["Views"]), [30, 10])

    def test_unknown_column_raises(self):
        with self.assertRaises(ValueError):
            self.service.filter(self.data, Missing="value")


class TestApiService(unittest.TestCase):
    def test_get_video_stats_returns_counts(self):
        response = Mock()
        response.json.return_value = {
            "items": [{"statistics": {"viewCount": "12", "likeCount": "3"}}]
        }

        with patch("ApiService.requests.get", return_value=response):
            service = ApiService()
            service.set_yt_api_key("key")

            stats = service.get_video_stats("video-id")

        self.assertEqual(stats, (12, 3))

    def test_get_recent_videos_requires_api_key(self):
        service = ApiService()

        with self.assertRaises(ValueError):
            service.getRecentVideos(Platform("YouTube", "key"), CreatorData("Creator", None))


class TestInstagramApiService(unittest.TestCase):
    def test_get_recent_videos_maps_profile_and_posts(self):
        response = Mock()
        response.json.return_value = {
            "data": {
                "user": {
                    "username": "creator",
                    "edge_followed_by": {"count": 1234},
                    "edge_owner_to_timeline_media": {
                        "edges": [{
                            "node": {
                                "shortcode": "ABC123",
                                "taken_at_timestamp": 1788307200,
                                "video_view_count": 987,
                                "edge_media_preview_like": {"count": 42},
                                "edge_media_to_caption": {
                                    "edges": [{"node": {"text": "A new post\nMore details"}}]
                                },
                            }
                        }]
                    },
                }
            }
        }
        response.raise_for_status.return_value = None
        client = Mock()
        client.get.return_value = response

        service = InstagramApiService(client=client)
        creator = service.getRecentVideos(
            Platform("Instagram", ""),
            CreatorData("@creator", None),
        )

        self.assertEqual(creator.name, "creator")
        self.assertEqual(creator.subscribers, 1234)
        self.assertEqual(creator.videos[0].title, "A new post")
        self.assertEqual(creator.videos[0].views, 987)
        self.assertEqual(creator.videos[0].likes, 42)
        client.get.assert_called_once()

    def test_rejects_non_instagram_platform(self):
        service = InstagramApiService(client=Mock())

        with self.assertRaises(ValueError):
            service.getRecentVideos(
                Platform("YouTube", "key"),
                CreatorData("creator", None),
            )

    @patch("instagram_api.time.sleep")
    def test_retries_rate_limit_and_uses_retry_after(self, sleep):
        rate_limited = Mock(status_code=429, headers={"Retry-After": "1"})
        success = Mock(status_code=200)
        success.json.return_value = {"data": {"user": {"username": "creator"}}}
        success.raise_for_status.return_value = None
        client = Mock()
        client.get.side_effect = [rate_limited, success]
        service = InstagramApiService(client=client, max_retries=1)

        profile = service.fetch_profile("creator")

        self.assertEqual(profile["data"]["user"]["username"], "creator")
        self.assertEqual(client.get.call_count, 2)
        sleep.assert_called_once_with(15.0)

    @patch("instagram_api.time.monotonic", side_effect=[0.0, 0.0, 1.0, 1.0, 1.0])
    def test_rate_limit_uses_last_cached_profile_and_only_returns_last_post(self, _monotonic):
        cached_response = Mock(status_code=200)
        cached_response.json.return_value = {
            "data": {
                "user": {
                    "username": "creator",
                    "edge_followed_by": {"count": 10},
                    "edge_owner_to_timeline_media": {
                        "edges": [
                            {"node": {"shortcode": "old"}},
                            {"node": {"shortcode": "last"}},
                        ]
                    },
                }
            }
        }
        cached_response.raise_for_status.return_value = None
        limited_response = Mock(status_code=429, headers={"Retry-After": "15"})
        client = Mock()
        client.get.side_effect = [cached_response, limited_response]
        service = InstagramApiService(client=client, cache_ttl=0.5)

        service.fetch_profile("creator")
        creator = service.getRecentVideos(
            Platform("Instagram", ""), CreatorData("creator", None)
        )

        self.assertEqual(len(creator.videos), 1)
        self.assertEqual(creator.videos[0].title, "last")
        self.assertIn("last cached post", service.last_status)

    def test_caches_profile_within_cache_ttl(self):
        response = Mock(status_code=200)
        response.json.return_value = {"data": {"user": {"username": "creator"}}}
        response.raise_for_status.return_value = None
        client = Mock()
        client.get.return_value = response
        service = InstagramApiService(client=client)

        service.fetch_profile("creator")
        service.fetch_profile("creator")

        client.get.assert_called_once()

    @patch("instagram_api.time.sleep")
    def test_search_never_exceeds_99_api_calls(self, _sleep):
        response = Mock(status_code=429, headers={})
        client = Mock()
        client.get.return_value = response
        service = InstagramApiService(client=client, max_retries=200)

        with self.assertRaises(RuntimeError):
            service.getRecentVideos(
                Platform("Instagram", ""), CreatorData("creator", None)
            )

        self.assertEqual(client.get.call_count, 99)

    def test_failed_search_saves_previous_data(self):
        response = Mock(status_code=500)
        client = Mock()
        client.get.return_value = response
        save_callback = Mock()
        previous_data = [CreatorData("creator", Platform("Instagram", ""))]
        service = InstagramApiService(
            client=client,
            save_callback=save_callback,
            data_provider=lambda: previous_data,
        )

        with self.assertRaises(Exception):
            service.getRecentVideos(
                Platform("Instagram", ""), CreatorData("creator", None)
            )

        save_callback.assert_called_once_with(previous_data)


if __name__ == "__main__":
    unittest.main()