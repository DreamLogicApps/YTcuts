import unittest

from pydantic import ValidationError

from backend.downloader import DownloadTask
from backend.metadata import validate_youtube_url
from backend.routes.download import DownloadRequest
from backend.routes import support


class SecurityBoundaryTests(unittest.TestCase):
    def test_accepts_supported_youtube_urls(self):
        self.assertEqual(
            validate_youtube_url("https://youtu.be/dQw4w9WgXcQ"),
            "https://youtu.be/dQw4w9WgXcQ",
        )
        self.assertEqual(
            validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    def test_rejects_non_youtube_targets(self):
        for url in (
            "http://127.0.0.1:8000/secret",
            "https://example.com/video",
            "file:///etc/passwd",
        ):
            with self.assertRaises(ValueError):
                validate_youtube_url(url)

    def test_download_request_rejects_invalid_ranges(self):
        with self.assertRaises(ValidationError):
            DownloadRequest(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                start_time="00:01:00",
                end_time="00:00:30",
            )

    def test_time_parser_rejects_malformed_clock_values(self):
        with self.assertRaises(ValueError):
            DownloadTask.parse_time("01:60")
        self.assertEqual(DownloadTask.parse_time("01:02:03"), 3723)

    def test_support_url_only_allows_buy_me_a_coffee_profile(self):
        original_url = support.BUYMEACOFFEE_URL
        original_mode = support.BUYMEACOFFEE_MODE
        try:
            support.BUYMEACOFFEE_URL = "https://buymeacoffee.com/example-user"
            self.assertIsNotNone(support.get_valid_support_url())
            support.BUYMEACOFFEE_URL = "https://example.com/example-user"
            self.assertIsNone(support.get_valid_support_url())
            support.BUYMEACOFFEE_URL = "http://buymeacoffee.com/example-user"
            self.assertIsNone(support.get_valid_support_url())
            support.BUYMEACOFFEE_MODE = "demo"
            self.assertEqual(support.get_support_checkout_url(), "/api/support/test-checkout")
            support.BUYMEACOFFEE_MODE = "live"
            support.BUYMEACOFFEE_URL = "https://buymeacoffee.com/example-user"
            self.assertEqual(
                support.get_support_checkout_url(),
                "https://buymeacoffee.com/example-user",
            )
        finally:
            support.BUYMEACOFFEE_URL = original_url
            support.BUYMEACOFFEE_MODE = original_mode


if __name__ == "__main__":
    unittest.main()
