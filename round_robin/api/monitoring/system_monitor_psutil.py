import psutil
from .system_monitoring_base import SystemMonitorBase

class PsutilSystemMonitor(SystemMonitorBase):
    """ Implementation of SystemMonitorBase using psutil """

    def get_cpu_usage(self):
        """ Returns CPU usage percentage using psutil """
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """ Returns memory usage percentage using psutil """
        return psutil.virtual_memory().percent
