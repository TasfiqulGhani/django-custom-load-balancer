import asyncio
from api.proxies.proxy import Proxy
from ..monitoring.health_checker import HealthChecker
from api.proxies.instance_manager import InstanceManager
from ..monitoring.system_monitor_docker import DockerSystemMonitor
from ..adapters.httpx_adapter import HttpxAdapter  # Import our HTTP adapter


class RoundRobinProxy(Proxy):
    """ Async Round Robin Proxy with Full Dependency Injection """

    current_index = 0

    def __init__(self, instance_manager, http_client, health_checker, system_monitor):
        """ Inject all dependencies instead of hardcoding them """
        self.instance_manager = instance_manager
        self.http_client = http_client
        self.system_monitor = system_monitor
        self.health_checker = health_checker  

    async def forward_request(self, data):
        """ Retries with another server asynchronously if the current one fails """
        healthy_instances = self.health_checker.get_healthy_instances()

        if not healthy_instances:
            print("🚨 No healthy instances available. Returning error response.", flush=True)
            return self.generate_error_response()

        total_servers = len(healthy_instances)
        if RoundRobinProxy.current_index >= total_servers:
            RoundRobinProxy.current_index = 0  # Reset index if out of range

        for _ in range(total_servers):
            instance_url = healthy_instances[RoundRobinProxy.current_index]
            response = await self.http_client.post(instance_url, json=data)

            if response is None:
                print(f"❌ Request to {instance_url} failed (HTTP client returned None). Skipping to next instance.")
                RoundRobinProxy.current_index = (RoundRobinProxy.current_index + 1) % total_servers
                continue  # Skip to the next server if response is None

            # Process response separately
            result = self.handle_response(response, instance_url, total_servers)
            if result:
                return result  # Return response if successful

        print("❌ All retries failed. Returning error response.")
        return self.generate_error_response()


    def handle_response(self, response, instance_url, total_servers):
        """ Handles HTTP response & determines next actions """
        
        if response and response.status_code == 200:
            RoundRobinProxy.current_index = (RoundRobinProxy.current_index + 1) % total_servers
            return response.json(), 200

        if response and response.status_code >= 500:
            print(f"⚠️ {instance_url} failed with {response.status_code}. Marking as failed & retrying.")
            self.health_checker.mark_failed(instance_url)

        
        RoundRobinProxy.current_index = (RoundRobinProxy.current_index + 1) % total_servers
        return None

