import http.client
import ssl
import unittest
import urllib.error
from unittest.mock import patch

from scripts.check_links import check


class LinkCheckerTests(unittest.TestCase):
    @patch("scripts.check_links.time.sleep")
    @patch("scripts.check_links.request")
    def test_connection_reset_is_retried_and_reported(self, request, sleep):
        request.side_effect = http.client.RemoteDisconnected("Connection closed")
        result = check("https://example.org/")
        self.assertEqual(result.outcome, "failed")
        self.assertEqual(request.call_count, 2)

    @patch("scripts.check_links.time.sleep")
    @patch("scripts.check_links.request")
    def test_certificate_failure_remains_a_failure(self, request, sleep):
        request.side_effect = urllib.error.URLError(ssl.SSLCertVerificationError("Invalid certificate"))
        result = check("https://example.org/")
        self.assertEqual(result.outcome, "failed")
        self.assertIn("Invalid certificate", result.detail)

    @patch("scripts.check_links.time.sleep")
    @patch("scripts.check_links.request")
    def test_connection_recovers_on_retry(self, request, sleep):
        request.side_effect = [ConnectionResetError("reset"), (200, "https://example.org/")]
        self.assertEqual(check("https://example.org/").outcome, "ok")

    @patch("scripts.check_links.request")
    def test_head_not_supported_falls_back_to_get(self, request):
        request.side_effect = [
            urllib.error.HTTPError("https://example.org/", 405, "Method not allowed", {}, None),
            (200, "https://example.org/"),
        ]
        self.assertEqual(check("https://example.org/").outcome, "ok")
        self.assertEqual(request.call_args.args[1], "GET")
