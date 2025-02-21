from ..adapters.docker_adapter import DockerAdapter


class InstanceManager:
    """Manages Application API instances dynamically from Docker"""

    def __init__(self):
        self.docker_adapter = DockerAdapter()
        self.instances = []
        self.failed_instances = set()
        self.refresh_instances()

    def refresh_instances(self):
        """Fetches all running instances from Docker"""
        self.instances = [
            f"http://{container}:8000/api/process/"
            for container in self.docker_adapter.get_running_containers()
        ]

    def mark_failed(self, instance_url):
        """Marks an instance as failed (adds it to the failed list)"""
        if instance_url not in self.failed_instances:
            print(f"❌ Marking {instance_url} as failed")
            self.failed_instances.add(instance_url)

    def mark_healthy(self, instance_url):
        """Marks an instance as healthy (removes from failed list)"""
        if instance_url in self.failed_instances:
            print(f"{instance_url} is back online! Removing from failed list.")
            self.failed_instances.remove(instance_url)

    def get_healthy_instances(self):
        """Returns only healthy instances for proxy selection"""
        return [inst for inst in self.instances if inst not in self.failed_instances]
