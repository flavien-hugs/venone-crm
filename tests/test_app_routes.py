from unittest.mock import patch

from tests.base_case import BaseCase


class TestApp(BaseCase):
    @patch("requests.get")
    def test_map_view(self, mock_get):
        response = self.client.get("/api/tenants/")
        self.assertEqual(response.status_code, 200)
