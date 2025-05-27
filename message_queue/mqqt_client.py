# import paho.mqtt.client as mqtt
from paho.mqtt import (client as mqtt, 
                       enums)
from typing import Callable, Any


# from BoitLogger.boit_logger import ServiceLogger
from BoitLogger.boit_logger import ServiceLogger

class Subscriber:
    def __init__(self, 
                 host:str, 
                 port:int, 
                 user_name:str, 
                 password:str, 
                 timeout:int=60):
        
        self._host:str = host
        self._port:int = port
        self._timeout:int = timeout
        self._topics:dict[str, Callable[[str, bytes], None]] = {}        
                        
        self._client = mqtt.Client(callback_api_version=enums.CallbackAPIVersion.VERSION2)
        self._client.username_pw_set(user_name, password)
        self._client.on_connect = self._on_connect
        self._client.on_connect_failed = self._on_connect_failed
        self._client.on_message = self._on_message
        
    @property
    def topics(self) -> dict[str, str]:
        return {k:v.__name__ for k, v in self._topics.items()}

    @property
    def is_connected(self)->bool:
        return self._client.is_connected()
    
    def start(self, timeout:int=60) -> None:
        ServiceLogger.log_info(__name__, f"Connecting to {self._host}:{self._port}")
        self._client.connect(self._host, self._port, timeout)
        self._client.loop_start()
        
    
    def stop(self) -> None:
        ServiceLogger.log_info(__name__, f"Disconnecting from {self._host}:{self._port}")
        self._client.loop_stop()
        self._client.disconnect()
        
    def add_topic(self, topic:str, callback:Callable[[str, bytes], None]) -> bool:
        if topic in self._topics.keys():
            ServiceLogger.log_error(__name__, f"{topic} already exists")
            return False
        
        ServiceLogger.log_info(__name__, f"{topic} - Callback Added")
        res = self._client.subscribe(topic)
        
        if res[0] != mqtt.MQTT_ERR_SUCCESS:
            ServiceLogger.log_error(__name__, f"Failed to subscribe to {topic} with error code {res}")            
            return False
        
        self._topics[topic] = callback        
        
        return True
    
    def remove_topic(self, topic:str) -> bool:
        if topic not in self._topics.keys():
            return True
        

        ServiceLogger.log_info(__name__, f"{topic} - Callback Removed")
        result = self._client.unsubscribe(topic)

        if result[0] != mqtt.MQTT_ERR_SUCCESS:
            ServiceLogger.log_error(__name__, f"Failed to unsubscribe from {topic} with error code {result}")
            return False
        
        del self._topics[topic]
        
        return True
    
    def clear_topics(self) -> None:        
        self._client.unsubscribe(list(self._topics.keys()))
        self._topics.clear()
        ServiceLogger.log_info(__name__, "All topics cleared")
        
    def __str__(self) -> str:
        return f"Subscriber: {self._host}:{self._port}, connected: {self.is_connected}"
        
    
    def _on_connect_failed(self, 
                            client:mqtt.Client, 
                            userdata:Any)->None:
        ServiceLogger.log_error(__name__, "Failed to connect to broker")
        
    def _on_connect(self, client:mqtt.Client, 
                   userdata:Any, 
                   flags:dict[str, Any], 
                   rc:mqtt.ReasonCode,
                   properties:mqtt.Properties|None=None)->None:
        ServiceLogger.log_info(__name__, f"Connected with result code {rc}")
        
    def _on_message(self, client:mqtt.Client, 
                     userdata:Any, 
                     msg:mqtt.MQTTMessage)->None:
        ServiceLogger.log_info(__name__, f"Received topic: {msg.topic}")
        
        for k, v in self._topics.items():
            # Check if the topic has a wildcard
            if "#" in k:
                if msg.topic.startswith(k[:-1]):
                    v(msg.topic, msg.payload)
            
            elif msg == k:
                v(msg.topic, msg.payload)
                
if __name__ == "__main__":
    print("Hiya")
                