from abc import ABC, abstractmethod

class SystemMonitorBase(ABC):
    """ Abstract Base Class for system resource monitoring """

    @abstractmethod
    def get_cpu_usage(self):
        """ Get current CPU usage percentage """
        pass

    @abstractmethod
    def get_memory_usage(self):
        """ Get current memory usage percentage """
        pass
