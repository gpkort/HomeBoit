# import aiomqtt
from abc import ABC, abstractmethod
from typing import Callable


class QueueListener(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.host:str = ""
        self.port:int = 0
        
        self.topics:dict[str, Callable[[str, bytes], None]] = {}
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
            self.topics[topic] = callback
            return True
        return False
    
    def remove_topic(self, topic:str) -> bool:
        cb:Callable[[str, bytes], None] | None = self.topics.pop(topic, None)
        
        return cb is not None
    
    def clear_topics(self) -> None:
        self.topics.clear()