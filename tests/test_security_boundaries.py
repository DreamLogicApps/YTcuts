import unittest
import shutil

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

    def test_progress_parser_updates_percent_speed_and_eta(self):
        task = DownloadTask(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            start_time="00:00:01",
            end_time="00:00:10",
        )
        try:
            task.parse_progress_line("YT_CUTS_PROGRESS| 42.5%|1.20MiB/s|00:08")
            self.assertEqual(task.progress, 42.5)
            self.assertEqual(task.speed, "1.20MiB/s")
            self.assertEqual(task.eta, "00:08")
        finally:
            shutil.rmtree(task.task_dir, ignore_errors=True)

    def test_legacy_progress_parser_updates_speed_and_eta(self):
        task = DownloadTask(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            start_time="00:00:01",
            end_time="00:00:10",
        )
        try:
            task.parse_progress_line("[download]  25.0% of 10.00MiB at 2.00MiB/s ETA 00:05")
            self.assertEqual(task.progress, 25.0)
            self.assertEqual(task.speed, "2.00MiB/s")
            self.assertEqual(task.eta, "00:05")
        finally:
            shutil.rmtree(task.task_dir, ignore_errors=True)

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
