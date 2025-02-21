import time
import threading
import requests
from django.conf import settings
from ..monitoring.system_monitor_docker import  DockerSystemMonitor
from ..adapters.docker_adapter import DockerAdapter

class HealthChecker:
    """ Monitors instances via Docker and prevents overloading failing servers """

    def __init__(self, instance_manager, system_monitor: DockerSystemMonitor):
        self.instance_manager = instance_manager
        self.system_monitor = system_monitor
        self.docker_adapter = DockerAdapter()
        self.instances = instance_manager.get_instances()
        self.failed_instances = set()  # Tracks failing instances
        self.running = True

        # Start background health check process
        self.health_check_thread = threading.Thread(target=self.health_check_loop, daemon=True)
        self.health_check_thread.start()
        print("🩺 Health Checker Thread Started!", flush=True)

    def health_check_loop(self):
        """ Runs every 5 seconds to check instance health and refresh instances """
        while self.running:
            time.sleep(settings.HEALTH_CHECK_INTERVAL)
            print("🔄 Checking health of instances and refreshing available ones...", flush=True)
            self.instances = self.instance_manager.get_instances()  # Fetch latest running instances
            self.check_instances_health()

    def check_instances_health(self):
        """ Checks if instances are running and removes them from the failed list if healthy """
        for instance_url in list(self.failed_instances):  # Check only failed instances
            container_name = instance_url.replace("http://", "").split(":")[0]

            is_running = self.docker_adapter.get_container_status(container_name) == "running"
            is_healthy = self.is_application_healthy(instance_url)

            # Skip CPU/Memory check if the container is not running
            if not is_running:
                print(f"🚨 {instance_url} is stopped. Marking as failed!", flush=True)
                self.failed_instances.add(instance_url)
                continue  # ❌ Skip this instance

            is_overloaded = self.is_container_overloaded(container_name)

            if is_running and not is_overloaded and is_healthy:
                print(f"{instance_url} has recovered! Removing from failure list.", flush=True)
                self.failed_instances.remove(instance_url)  

    def is_application_healthy(self, instance_url):
        """ Checks if the application is responding to health check API """
        health_url = instance_url.replace("/api/process/", "/api/process/health")

        try:
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200  # Healthy if it returns 200 OK
        except requests.exceptions.RequestException:
            print(f"🚨 {instance_url} failed health check!", flush=True)
            return False

    def is_container_overloaded(self, container_name):
        """ Uses DockerSystemMonitor to check CPU & Memory usage """
        cpu_usage = self.system_monitor.get_cpu_usage(container_name)
        memory_usage = self.system_monitor.get_memory_usage(container_name)

        # Skip CPU/Memory check if container is missing or stopped
        if cpu_usage is None or memory_usage is None:
            print(f"⚠️ Skipping CPU/Memory check for {container_name}.", flush=True)
            return False  # Consider it NOT overloaded

        print(f"🖥️ {container_name} → CPU: {cpu_usage}%, Memory: {memory_usage}%", flush=True)

        return cpu_usage > settings.CPU_THRESHOLD or memory_usage > settings.MEMORY_THRESHOLD  # ❌ Mark as failed if overloaded

    def mark_failed(self, instance_url):
        """ Adds instance to the failed list (Used when request fails) """
        print(f"❌ Marking {instance_url} as failed due to request failure!", flush=True)
        self.failed_instances.add(instance_url)

    def get_healthy_instances(self):
        """Returns only healthy instances for proxy selection"""
        return [inst for inst in self.instances if inst not in self.failed_instances]
    
    def stop(self):
        """ Gracefully stop the health checker """
        self.running = False
