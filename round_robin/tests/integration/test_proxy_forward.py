import json
from django.test import TestCase, Client
from unittest.mock import AsyncMock, patch

class ProxyForwardRequestIntegrationTest(TestCase):
    """ Integration tests for the proxy forwarding API """

    def setUp(self):
        """ Set up a Django test client """
        self.client = Client()

    @patch("api.apis.proxy")
    @patch("api.apis.RequestHandler.handle_request", new_callable=AsyncMock)
    def test_proxy_forward_success(self, mock_handle_request, mock_proxy):
        """ Test successful proxy forwarding """
        mock_handle_request.return_value = ({"success": True}, 200)

        response = self.client.post(
            "/api/process/",
            json.dumps({"test": "data"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})
        mock_handle_request.assert_called_once()

    @patch("api.apis.proxy")
    @patch("api.apis.RequestHandler.handle_request", new_callable=AsyncMock)
    def test_proxy_forward_proxy_failure(self, mock_handle_request, mock_proxy):
        """ Test proxy returning an error response """
        mock_handle_request.return_value = ({"error": "Proxy failure"}, 502)

        response = self.client.post(
            "/api/process/",
            json.dumps({"test": "data"}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {"error": "Proxy failure"})

    def test_proxy_forward_invalid_json(self):
        """ Test handling of invalid JSON input """
        response = self.client.post(
            "/api/process/",
            "invalid json data",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON"})

    def test_proxy_forward_get_request(self):
        """ Ensure only POST requests are allowed """
        response = self.client.get("/api/process/")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json(), {"error": "Only POST allowed"})
