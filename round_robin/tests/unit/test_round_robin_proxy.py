import unittest
from unittest.mock import AsyncMock, MagicMock
from api.proxies.round_robin import RoundRobinProxy

class TestRoundRobinProxy(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        """Setup mock dependencies before each test."""
        self.mock_instance_manager = MagicMock()
        self.mock_http_client = AsyncMock()
        self.mock_health_checker = MagicMock()
        self.mock_system_monitor = MagicMock()

        self.proxy = RoundRobinProxy(
            instance_manager=self.mock_instance_manager,
            http_client=self.mock_http_client,
            health_checker=self.mock_health_checker,
            system_monitor=self.mock_system_monitor,
        )

    async def test_forward_request_success(self):
        """Test if request is forwarded successfully"""
        self.mock_instance_manager.get_healthy_instances.return_value = ["http://server1:8000/api/process"]

        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
        self.mock_http_client.post.return_value = mock_response

        response, status = await self.proxy.forward_request({"test": "data"})

        self.assertEqual(response, {"success": True})
        self.assertEqual(status, 200)

    async def test_forward_request_all_servers_fail(self):
        """Test behavior when all servers fail"""
        self.mock_instance_manager.get_healthy_instances.return_value = ["http://server1:8000/api/process"]

        # Mock response with failure (simulate all servers failing)
        self.mock_http_client.post.return_value = None

        response, status = await self.proxy.forward_request({"test": "data"})

        self.assertEqual(response["status"], "error")
        self.assertEqual(status, 503)

    async def test_forward_request_http_client_failure(self):
        """Test if a request fails due to HTTP client returning None"""
        self.mock_instance_manager.get_healthy_instances.return_value = [
            "http://server1:8000/api/process",
            "http://server2:8000/api/process"
        ]

        # Simulate HTTP failure by returning None
        self.mock_http_client.post.return_value = None

        response, status = await self.proxy.forward_request({"test": "data"})

        self.assertEqual(response["status"], "error")
        self.assertEqual(status, 503)

    def test_handle_response_success(self):
        """Test handling of successful response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        result, status = self.proxy.handle_response(mock_response, "http://server1:8000/api/process", 3)

        self.assertEqual(result, {"success": True})
        self.assertEqual(status, 200)

    async def test_forward_request_with_retries_success_on_third_attempt(self):
        """Test if request fails twice and succeeds on the third attempt"""
        self.mock_instance_manager.get_healthy_instances.return_value = [
            "http://server1:8000/api/process",
            "http://server2:8000/api/process",
            "http://server3:8000/api/process"
        ]

        # Simulate first two attempts failing (returning None)
        mock_response_fail = None

        # Simulate third attempt succeeding
        mock_response_success = AsyncMock()
        mock_response_success.status_code = 200
        mock_response_success.json = MagicMock(return_value={"success": True})

        # Mock HTTP client to fail twice, then succeed
        self.mock_http_client.post.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]

        response, status = await self.proxy.forward_request({"test": "data"})

        # Verify that the third attempt succeeded
        self.assertEqual(response, {"success": True})
        self.assertEqual(status, 200)