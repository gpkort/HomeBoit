from abc import ABC, abstractmethod
from typing import Callable


class QueueListener(ABC):
    def __init__(self, host:str, port:int) -> None:
        super().__init__()
        self.__host:str = host
        self.__port:int = port
        
        self.__topics:dict[str, Callable[[str, bytes], None]] = {}
        
    @property
    def topics(self) -> dict[str, str]:
        return {k:v.__name__ for k, v in self.__topics.items()}
    
    def __str__(self) -> str:
        return f"Subscriber: {self.__host}:{self.__port}"
        
    @abstractmethod
    def start(self) -> None:
        """Start the listener for the given topic and callback."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the listener."""
        pass
    
    def add_topic(self, topic:str, callback:Callable[[str, bytes], None]) -> bool:
        if topic not in self.topics.keys():
            self.__topics[topic] = callback
            return True
        return False
    
    def remove_topic(self, topic:str) -> bool:
        cb:Callable[[str, bytes], None] | None = self.__topics.pop(topic, None)
        
        return cb is not None
    
    def clear_topics(self) -> None:
        self.topics.clear()