import paho.mqtt.client as mqtt
import aiomqtt

from dataclasses import dataclass
from typing import Callable

from ServoLogger.servo_logger import ServiceLogger
from . topics import MQTT_WILDCARD, SERVO_PREFIX

@dataclass
class TopicCallback:
    topic:str
    callback:Callable[[str, bytes], None]    
    
class AsyncSubscriber:
    def __init__(self,
                 host:str, 
                 port:int, 
                 user_name:str, 
                 password:str,
                 keepalive:int=60):
        self.__host:str = host
        self.__port = port
        self.__user_name = user_name
        self.__password = password
        self.__keepalive = keepalive
        
    async def start(self, *, topic:str, callback:Callable[[str, bytes], None])->None:
        async with aiomqtt.Client(hostname=self.__host,
                                  port=self.__port,
                                  username=self.__user_name,
                                  password=self.__password,
                                  keepalive=self.__keepalive) as client:
            
            await client.subscribe(topic)
            async for message in client.messages:
                ServiceLogger.log_info(__name__, f"Received topic: {message.topic}")
                callback(message.topic.value, message.payload)
                


class Subscriber:
    def __init__(self, 
                 host:str, 
                 port:int, 
                 user_name:str, 
                 password:str, 
                 timeout:int=60):
        
        self.__host:str = host
        self.__port = port
        self.__callbacks:list[TopicCallback] = []
        
        self.__client = mqtt.Client()
        self.__client.username_pw_set(user_name, password)
        self.__client.on_connect = self.__on_connect
        self.__client.on_connect_failed = self.__on_connect_failed
        self.__client.on_message = self.__on_message

    @property
    def is_connected(self)->bool:
        return self.__client.is_connected()
    
    def start(self, timeout:int=60) -> None:
        ServiceLogger.log_info(__name__, f"Connecting to {self.__host}:{self.__port}")
        self.__client.connect(self.__host, self.__port, timeout)
        self.__client.loop_forever()
    
    def set_callbacks(self, cbs: list[TopicCallback])->None:
        self.__callbacks.clear()
        self.add_callbacks(cbs)     
    
    def add_callbacks(self, cbs: list[TopicCallback])->None:
        self.__callbacks = cbs
        
    def add_callback(self, cb:TopicCallback)->None:        
        self.__callbacks.append(cb)        
        ServiceLogger.log_info(__name__, f"{cb.topic} - Callback Added")

    def __str__(self) -> str:
        return f"Subscriber: {self.__host}:{self.__port}, connected: {self.is_connected}"
        
    
    def __on_connect_failed(self, 
                            client:mqtt.Client, 
                            userdata:any)->None:
        ServiceLogger.log_error(__name__, "Failed to connect to broker")
        
    def __on_connect(self, client:mqtt.Client, 
                   userdata:any, 
                   flags:dict[str, any], 
                   rc:mqtt.ReasonCode,
                   properties:mqtt.Properties|None=None)->None:
        ServiceLogger.log_info(__name__, f"Connected with result code {rc}")
        self.__client.subscribe(f"{SERVO_PREFIX}/{MQTT_WILDCARD}")
        
    def __on_message(self, client:mqtt.Client, userdata:any, msg:mqtt.MQTTMessage)->None:
        ServiceLogger.log_info(__name__, f"Received topic: {msg.topic}")
        
        for cb in self.__callbacks:
            if "#" in cb.topic:
                if msg.topic.startswith(cb.topic[:-1]):
                    cb.callback(msg.topic, msg.payload)
            
            elif msg.topic == cb.topic:
                cb.callback(msg.topic, msg.payload)
                