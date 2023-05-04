from tests.base_case import BaseCase


class TestChartApp(BaseCase):

    def test_get_owners_data(self):

        response = self.client.get('/api/owners/data/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(all(isinstance(d, dict) and 'year' in d and 'month' in d and 'count' in d for d in data))

    def test_get_tenants_data(self):

        response = self.client.get('/api/tenants/data/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(all(isinstance(d, dict) and 'year' in d and 'month' in d and 'count' in d for d in data))
