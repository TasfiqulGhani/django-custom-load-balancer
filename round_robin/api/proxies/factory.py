from django.conf import settings
from .round_robin import RoundRobinProxy
from .instance_manager import InstanceManager
from ..monitoring.health_checker import HealthChecker
from ..monitoring.system_monitor_docker import DockerSystemMonitor
from ..adapters.httpx_adapter import HttpxAdapter

class ProxyFactory:
    """ Factory to create different proxy strategies with dependency injection """

    @staticmethod
    def create_round_robin_proxy():
        """ Creates a Round Robin Proxy with all dependencies injected """
        instance_manager = InstanceManager()
        http_adapter = HttpxAdapter()
        system_monitor = DockerSystemMonitor()
        health_checker = HealthChecker(instance_manager, system_monitor)

        return RoundRobinProxy(instance_manager, http_adapter, health_checker, system_monitor)

    @staticmethod
    def get_proxy():
        """ Selects proxy strategy and injects dependencies """
        strategy = settings.PROXY_STRATEGY
        print(f"🔹 Selected Proxy Strategy: {strategy}")

        if strategy == "round_robin":
            return ProxyFactory.create_round_robin_proxy()
        else:
            raise ValueError("❌ Invalid Proxy Strategy in .env")
