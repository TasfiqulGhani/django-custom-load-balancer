from ..adapters.docker_adapter import DockerAdapter


class InstanceManager:
    """Manages Application API instances dynamically from Docker"""

    def __init__(self):
        self.docker_adapter = DockerAdapter()

    def get_instances(self):
        """Fetches all running instances from Docker"""
        return [
            f"http://{container}:8000/api/process/"
            for container in self.docker_adapter.get_running_containers()
        ]
