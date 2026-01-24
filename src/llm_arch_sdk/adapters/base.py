from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    @abstractmethod
    def client(self):
        pass
