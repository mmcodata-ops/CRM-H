from django.test import TestCase, Client

class DashboardLiveSyncTests(TestCase):
    def test_dashboard_live_api_returns_data(self):
        client = Client()
        response = client.get('/api/dashboard-live/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('hg', data)
        self.assertIn('hetalls', data)
        self.assertTrue(len(data['hg']['raw_rows']) > 0)
