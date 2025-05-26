import pytest 
from unittest.mock import patch, Mock, MagicMock
from message_queue.mqqt_client import Subscriber
from typing import Generator
from paho.mqtt import client as mqtt

class TestSubscriber():
    
    @pytest.fixture
    def MQSubscriber(self) -> Generator[Subscriber, None, None]:
        with patch('paho.mqtt.client') as mock_client:
            mock_client.Client = MagicMock()
            mock_client.Client.connect = MagicMock()
            mock_client.Client.is_connected().return_value = True
            
            subscriber = Subscriber(
                host="localhost",
                port=1883,
                user_name="test_user",
                password="test_password"
            )
            subscriber._client = mock_client.Client
            
            yield subscriber
            
    def test_start(self, MQSubscriber):
        MQSubscriber.start(timeout=60)        
        MQSubscriber._client.connect.assert_called_once_with("localhost", 1883, 60)
        MQSubscriber._client.loop_start.assert_called_once()
        
    def test_add_topic(self, MQSubscriber):
        def mock_callback(topic: str, payload: bytes):
            pass
        MQSubscriber._client.subscribe = Mock(return_value=(mqtt.MQTT_ERR_SUCCESS, 1))
        
        result = MQSubscriber.add_topic("test/topic", mock_callback)
        
        assert result is True
        assert "test/topic" in MQSubscriber.topics.keys()
    
    def test_remove_topic(self, MQSubscriber):
        def mock_callback(topic: str, payload: bytes):
            pass
        
        MQSubscriber.add_topic("test/topic", mock_callback)
        result = MQSubscriber.remove_topic("test/topic")
        
        assert result is True
        assert "test/topic" not in MQSubscriber.topics
        MQSubscriber._client.unsubscribe.assert_called_once_with("test/topic")
        
        
        

