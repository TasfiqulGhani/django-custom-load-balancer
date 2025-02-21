import docker


class DockerSystemMonitor:
    """Monitors CPU and Memory usage of Docker containers"""

    def __init__(self):
        self.client = docker.from_env()

    def get_cpu_usage(self, container_name):
        """Returns CPU usage percentage using Docker stats"""
        try:
            container = self.client.containers.get(container_name)

            # If the container is NOT running, don't check CPU usage
            if container.status != "running":
                print(
                    f"🚨 {container_name} is not running. Skipping CPU check.",
                    flush=True,
                )
                return None
            stats = container.stats(stream=False)
            return (
                self.calculate_cpu_usage(stats) if stats else None
            )  # If stats missing, return None
        except docker.errors.NotFound:
            print(
                f"🚨 {container_name} does not exist. Skipping CPU check.", flush=True
            )
            return None
        except docker.errors.APIError:
            return None

    def calculate_cpu_usage(self, stats):
        """Calculates CPU usage percentage from Docker stats"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = stats["cpu_stats"].get("system_cpu_usage", 0) - stats[
                "precpu_stats"
            ].get("system_cpu_usage", 0)

            if system_delta > 0:
                return round((cpu_delta / system_delta) * 100.0, 2)
            else:
                return None
        except KeyError as e:
            print(f"⚠️ Missing CPU stat {e}, skipping CPU check.", flush=True)
            return None

    def get_memory_usage(self, container_name):
        """Returns Memory usage percentage using Docker stats"""
        try:
            container = self.client.containers.get(container_name)

            # If the container is NOT running, don't check Memory usage
            if container.status != "running":
                print(
                    f"🚨 {container_name} is not running. Skipping Memory check.",
                    flush=True,
                )
                return None
            stats = container.stats(stream=False)

            if (
                "memory_stats" in stats
                and "usage" in stats["memory_stats"]
                and "limit" in stats["memory_stats"]
            ):
                mem_usage = stats["memory_stats"]["usage"]
                mem_limit = stats["memory_stats"]["limit"]
                return (
                    round((mem_usage / mem_limit) * 100, 2) if mem_limit > 0 else None
                )

            return None
        except docker.errors.NotFound:
            print(
                f"🚨 {container_name} does not exist. Skipping Memory check.",
                flush=True,
            )
            return None
        except docker.errors.APIError:
            return None
