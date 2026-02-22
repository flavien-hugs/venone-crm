from unittest.mock import patch

from tests.base_case import BaseCase


class TestApp(BaseCase):
    @patch("src.tenant.models.current_user")
    @patch("src.api.house.current_user")
    @patch("requests.get")
    def test_available_houses_view(self, mock_get, mock_api_user, mock_model_user):
        mock_api_user.id = self.user.id
        mock_api_user.is_authenticated = True
        mock_model_user.id = self.user.id
        mock_model_user.is_authenticated = True
        response = self.client.get("/api/available-houses/")
        self.assertEqual(response.status_code, 200)

    @patch("src.tenant.models.current_user")
    @patch("src.api.house.current_user")
    def test_get_houses_listing(self, mock_api_user, mock_model_user):
        mock_api_user.id = self.user.id
        mock_api_user.is_authenticated = True
        mock_model_user.id = self.user.id
        mock_model_user.is_authenticated = True
        response = self.client.get("/api/available-houses/")
        self.assertEqual(response.status_code, 200)
