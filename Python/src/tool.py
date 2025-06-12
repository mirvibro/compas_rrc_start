from abc import ABC, abstractmethod

class Tool(ABC):
    @abstractmethod
    def grab(self):
        pass

    @abstractmethod
    def release(self):
        pass
