import unittest
from unittest.mock import MagicMock, patch
import time
from api.monitoring.health_checker import HealthChecker

class TestHealthChecker(unittest.TestCase):

    def setUp(self):
        """ Set up mocks for instance manager, Docker system monitor, and Docker adapter. """
        self.mock_instance_manager = MagicMock()
        self.mock_system_monitor = MagicMock()

        # Mock DockerAdapter methods
        with patch("api.monitoring.health_checker.DockerAdapter") as MockDockerAdapter:
            self.mock_docker_adapter = MockDockerAdapter.return_value
            self.health_checker = HealthChecker(self.mock_instance_manager, self.mock_system_monitor)

    def test_health_checker_initialization(self):
        """ Ensures health checker starts correctly. """
        self.assertTrue(self.health_checker.running)
        self.assertTrue(self.health_checker.health_check_thread.is_alive())

    @patch("api.monitoring.health_checker.requests.get")
    def test_is_application_healthy_success(self, mock_get):
        """ Test that a healthy application returns True """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        instance_url = "http://mockserver:8000/api/process/"
        result = self.health_checker.is_application_healthy(instance_url)

        self.assertTrue(result)
        mock_get.assert_called_with("http://mockserver:8000/api/process/health", timeout=5)


    def test_is_container_overloaded_not_overloaded(self):
        """ Test that a non-overloaded container returns False """
        self.mock_system_monitor.get_cpu_usage.return_value = 50
        self.mock_system_monitor.get_memory_usage.return_value = 60

        result = self.health_checker.is_container_overloaded("mock_container")
        self.assertFalse(result)

    def test_is_container_overloaded_high_cpu(self):
        """ Test that an overloaded container (CPU > 80%) returns True """
        self.mock_system_monitor.get_cpu_usage.return_value = 85
        self.mock_system_monitor.get_memory_usage.return_value = 60

        result = self.health_checker.is_container_overloaded("mock_container")
        self.assertTrue(result)

    def test_is_container_overloaded_high_memory(self):
        """ Test that an overloaded container (Memory > 80%) returns True """
        self.mock_system_monitor.get_cpu_usage.return_value = 50
        self.mock_system_monitor.get_memory_usage.return_value = 90

        result = self.health_checker.is_container_overloaded("mock_container")
        self.assertTrue(result)

    def test_is_container_overloaded_missing_data(self):
        """ Test that a missing container skips overload check """
        self.mock_system_monitor.get_cpu_usage.return_value = None
        self.mock_system_monitor.get_memory_usage.return_value = None

        result = self.health_checker.is_container_overloaded("mock_container")
        self.assertFalse(result)

    def test_mark_failed(self):
        """ Test that a failed instance is correctly marked """
        instance_url = "http://mockserver:8000/api/process/"
        self.health_checker.mark_failed(instance_url)

        self.assertIn(instance_url, self.health_checker.failed_instances)

    def test_check_instances_health_recovers(self):
        """ Test that a previously failed instance recovers when healthy """
        instance_url = "http://mockserver:8000/api/process/"
        self.health_checker.failed_instances.add(instance_url)

        self.mock_docker_adapter.get_container_status.return_value = "running"
        self.mock_system_monitor.get_cpu_usage.return_value = 50
        self.mock_system_monitor.get_memory_usage.return_value = 50

        with patch.object(self.health_checker, "is_application_healthy", return_value=True):
            self.health_checker.check_instances_health()

        self.assertNotIn(instance_url, self.health_checker.failed_instances)

    def test_check_instances_health_stays_failed(self):
        """ Test that a failed instance stays in the list if still unhealthy """
        instance_url = "http://mockserver:8000/api/process/"
        self.health_checker.failed_instances.add(instance_url)

        self.mock_docker_adapter.get_container_status.return_value = "stopped"

        self.health_checker.check_instances_health()
        self.assertIn(instance_url, self.health_checker.failed_instances)

    def test_stop_health_checker(self):
        """ Ensures that stopping the health checker sets `running` to False. """
        self.health_checker.stop()
        self.assertFalse(self.health_checker.running)
