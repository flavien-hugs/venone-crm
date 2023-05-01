from unittest.mock import patch

from tests.base_case import BaseCase


class TestApp(BaseCase):
    @patch("requests.get")
    def test_available_houses_view(self, mock_get):
        response = self.client.get("/api/available-houses/")
        self.assertEqual(response.status_code, 200)
