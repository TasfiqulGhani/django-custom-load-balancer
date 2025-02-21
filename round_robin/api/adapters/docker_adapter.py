import docker


class DockerAdapter:
    """Adapter for managing Docker API interactions"""

    def __init__(self):
        self.client = docker.from_env()

    def get_running_containers(self, prefix="app"):
        """Returns a list of running containers matching a prefix"""
        return [
            container.name
            for container in self.client.containers.list()
            if prefix in container.name
        ]

    def get_container_status(self, container_name):
        """Returns the status of a specific container"""
        try:
            container = self.client.containers.get(container_name)
            return container.status  # Returns 'running' or other states
        except docker.errors.NotFound:
            return "stopped"

    def get_container_stats(self, container_name):
        """Returns CPU & Memory stats for a specific container"""
        try:
            return self.client.containers.get(container_name).stats(stream=False)
        except docker.errors.APIError:
            return None
