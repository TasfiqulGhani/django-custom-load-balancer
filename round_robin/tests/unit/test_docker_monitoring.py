import unittest
from unittest.mock import MagicMock, patch
import docker
from api.monitoring.system_monitor_docker import DockerSystemMonitor

class TestDockerSystemMonitor(unittest.TestCase):

    def setUp(self):
        """ Set up mock Docker client and system monitor """
        self.mock_client = MagicMock()
        self.monitor = DockerSystemMonitor()
        self.monitor.client = self.mock_client  # Override with mock client

    def test_get_cpu_usage_running_container(self):
        """ Test CPU usage retrieval for a running container """
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_container.stats.return_value = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 200000},
                "system_cpu_usage": 1000000,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 100000},
                "system_cpu_usage": 800000,
            },
        }
        self.mock_client.containers.get.return_value = mock_container

        result = self.monitor.get_cpu_usage("mock_container")

        # Debugging: Print expected and actual results
        expected_cpu_usage = ((200000 - 100000) / (1000000 - 800000)) * 100 
        self.assertEqual(result, expected_cpu_usage)  # Use computed expected value


    def test_get_cpu_usage_stopped_container(self):
        """Test CPU usage returns None for a stopped container """
        mock_container = MagicMock()
        mock_container.status = "exited"  # Not running
        self.mock_client.containers.get.return_value = mock_container

        result = self.monitor.get_cpu_usage("mock_container")
        self.assertIsNone(result)

    def test_get_cpu_usage_nonexistent_container(self):
        """Test CPU usage returns None for a non-existent container """
        self.mock_client.containers.get.side_effect = docker.errors.NotFound("Container not found")

        result = self.monitor.get_cpu_usage("mock_container")
        self.assertIsNone(result)

    def test_get_cpu_usage_api_error(self):
        """Test CPU usage returns None when Docker API fails """
        self.mock_client.containers.get.side_effect = docker.errors.APIError("Docker API failure")

        result = self.monitor.get_cpu_usage("mock_container")
        self.assertIsNone(result)

    def test_calculate_cpu_usage_valid_data(self):
        """ Test valid CPU calculation """
        stats = {
            "cpu_stats": {
                "cpu_usage": {"total_usage": 500000},
                "system_cpu_usage": 2000000,
            },
            "precpu_stats": {
                "cpu_usage": {"total_usage": 300000},
                "system_cpu_usage": 1500000,
            },
        }

        result = self.monitor.calculate_cpu_usage(stats)
        self.assertEqual(result, 40.0)  # ((500k-300k) / (2M-1.5M)) * 100

    def test_calculate_cpu_usage_missing_data(self):
        """Test CPU calculation skips invalid data """
        stats = {"cpu_stats": {}, "precpu_stats": {}}

        result = self.monitor.calculate_cpu_usage(stats)
        self.assertIsNone(result)

    def test_get_memory_usage_running_container(self):
        """ Test Memory usage retrieval for a running container """
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_container.stats.return_value = {
            "memory_stats": {
                "usage": 500000000,  # 500 MB
                "limit": 1000000000,  # 1 GB
            }
        }
        self.mock_client.containers.get.return_value = mock_container

        result = self.monitor.get_memory_usage("mock_container")
        self.assertEqual(result, 50.0)  # Expected: (500MB / 1GB) * 100

    def test_get_memory_usage_stopped_container(self):
        """Test Memory usage returns None for a stopped container """
        mock_container = MagicMock()
        mock_container.status = "exited"  # Not running
        self.mock_client.containers.get.return_value = mock_container

        result = self.monitor.get_memory_usage("mock_container")
        self.assertIsNone(result)

    def test_get_memory_usage_nonexistent_container(self):
        """Test Memory usage returns None for a non-existent container """
        self.mock_client.containers.get.side_effect = docker.errors.NotFound("Container not found")

        result = self.monitor.get_memory_usage("mock_container")
        self.assertIsNone(result)

    def test_get_memory_usage_api_error(self):
        """Test Memory usage returns None when Docker API fails """
        self.mock_client.containers.get.side_effect = docker.errors.APIError("Docker API failure")

        result = self.monitor.get_memory_usage("mock_container")
        self.assertIsNone(result)
