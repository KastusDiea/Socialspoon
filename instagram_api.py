"""Instagram data service used by the creator intelligence application.

The service uses Instagram's public web profile endpoint. It deliberately does
not make a request at import time; callers control when network access occurs.
"""

from datetime import datetime
import time

import requests

from DataService import CreatorData, Video


class InstagramApiService:
    """Fetch a creator profile and its latest Instagram posts."""

    PROFILE_URL = "https://www.instagram.com/api/v1/users/web_profile_info/"
    MAX_REQUESTS_PER_SEARCH = 99
    RATE_LIMIT_WAIT = 15.0
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459",
    }

    def __init__(self, api_key=None, client=None, timeout=20.0, max_retries=0, cache_ttl=300.0, save_callback=None, data_provider=None):
        self.api_key = api_key
        self.client = client or requests
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        self._profile_cache = {}
        self._next_request_at = 0.0
        self._used_cached_profile = False
        self.last_status = ""
        self._requests_this_search = 0
        self.save_callback = save_callback
        self.data_provider = data_provider

    def getRecentVideos(self, platform, creator_name):
        """Return the latest Instagram posts as a :class:`CreatorData` object."""
        self._validate_request(platform, creator_name)
        self._requests_this_search = 0
        username = creator_name.get_name().strip().lstrip("@").rstrip("/").lower()
        try:
            profile = self.fetch_profile(username)
            user = self._extract_user(profile)
            posts = self._extract_posts(user)
            if self._used_cached_profile:
                posts = posts[-1:]
                self.last_status = "Instagram rate limit reached; showing the last cached post."
            else:
                self.last_status = "Instagram data loaded successfully."

            videos = [self._post_to_video(post) for post in posts]
            return CreatorData(
                name=user.get("username") or username,
                platform=platform,
                subscribers=self._integer(user.get("edge_followed_by", {}).get("count")),
                videos=videos,
            )
        except Exception:
            self._save_previous_data()
            raise

    def _save_previous_data(self):
        if self.save_callback is None or self.data_provider is None:
            return
        self.save_callback(self.data_provider())

    def fetch_profile(self, username):
        self._used_cached_profile = False
        username = username.strip().lstrip("@").rstrip("/").lower()
        cached = self._profile_cache.get(username)
        if cached and time.monotonic() - cached[0] < self.cache_ttl:
            return cached[1]

        for attempt in range(self.max_retries + 1):
            self._wait_for_next_request()
            if self._requests_this_search >= self.MAX_REQUESTS_PER_SEARCH:
                raise RuntimeError(
                    "Instagram request limit reached for this search (maximum 99 calls)."
                )
            self._requests_this_search += 1
            response = self.client.get(
                self.PROFILE_URL,
                params={"username": username},
                headers=self.DEFAULT_HEADERS,
                timeout=self.timeout,
            )
            if response.status_code != 429:
                response.raise_for_status()
                profile = response.json()
                self._profile_cache[username] = (time.monotonic(), profile)
                return profile

            if cached:
                self._next_request_at = time.monotonic() + self.RATE_LIMIT_WAIT
                self._used_cached_profile = True
                return cached[1]
            if attempt == self.max_retries:
                self._next_request_at = time.monotonic() + self.RATE_LIMIT_WAIT
                raise RuntimeError(
                    "Instagram rate limit reached. Please wait 15 seconds before trying again."
                )
            time.sleep(self._retry_delay(response, attempt))

        raise RuntimeError("Instagram profile request failed")

    def _wait_for_next_request(self):
        delay = self._next_request_at - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        self._next_request_at = 0.0

    @staticmethod
    def _retry_delay(response, attempt):
        retry_after = response.headers.get("Retry-After")
        try:
            return max(InstagramApiService.RATE_LIMIT_WAIT, float(retry_after))
        except (AttributeError, TypeError, ValueError):
            return InstagramApiService.RATE_LIMIT_WAIT

    @staticmethod
    def _validate_request(platform, creator_name):
        if platform is None:
            raise ValueError("Platform cannot be null")
        if platform.get_name() != "Instagram":
            raise ValueError("InstagramApiService requires an Instagram platform")
        if creator_name is None or not creator_name.get_name().strip():
            raise ValueError("Creator name cannot be empty")

    @staticmethod
    def _extract_user(profile):
        user = profile.get("data", {}).get("user")
        if not user:
            raise ValueError("Instagram profile not found")
        return user

    @staticmethod
    def _extract_posts(user):
        timeline = user.get("edge_owner_to_timeline_media", {})
        return [edge.get("node", {}) for edge in timeline.get("edges", [])[:10]]

    @classmethod
    def _post_to_video(cls, post):
        caption_edges = post.get("edge_media_to_caption", {}).get("edges", [])
        caption = caption_edges[0].get("node", {}).get("text", "") if caption_edges else ""
        title = caption.splitlines()[0].strip() if caption.strip() else post.get("shortcode", "Instagram post")
        timestamp = post.get("taken_at_timestamp")
        upload_date = ""
        if timestamp:
            upload_date = datetime.fromtimestamp(timestamp).date().isoformat()

        return Video(
            title=title,
            views=cls._integer(post.get("video_view_count")),
            likes=cls._integer(post.get("edge_media_preview_like", {}).get("count")),
            upload_date=upload_date,
        )

    @staticmethod
    def _integer(value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0





