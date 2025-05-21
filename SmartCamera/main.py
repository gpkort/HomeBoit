import configparser 
import asyncio
from QueueListener import topics

from ServoModel import servo_model as sm, servo_ws as ws 
from ServoLogger.servo_logger import ServiceLogger 
from QueueListener import servo_subscriber, topics

CONFIG_FILE = "config.ini"

config: configparser.ConfigParser = None
servo_model: sm.Servos2DOF = None
servo_listener: servo_subscriber.Subscriber = None
servo_webservice: ws.WS_Servo = None
servo_async_listener: servo_subscriber.AsyncSubscriber = None


def handle_servo_message_cb(topic:str, message:bytes):
    global servo_model, servo_webservice
    try:
        ServiceLogger.log_info(__name__, f"Servo Data: {message.decode()}")
        sdata = topics.ServoData.from_json_bytes(message)
        
        if sdata is None:
            ServiceLogger.log_error(__name__, f"Error creating Servo from message for {topic}") 
            return None        
        
        short_topic = topic[topic.index(f"{topics.SERVO_PREFIX}"):]
        ServiceLogger.log_info(__name__, f"data for {short_topic}: {sdata}")
        
        if short_topic == topics.INCREMENT:
            servo_model.increment_servo_angle(sdata.orientation, sdata.angle)            
        elif short_topic == topics.DECREMENT:
            servo_model.decrement_servo_angle(sdata.orientation, sdata.angle)
        elif short_topic == topics.SET:
            servo_model.set_servo_angle(sdata.orientation, sdata.angle)
        else:
            ServiceLogger.log_error(__name__, f"Unknown topic {topic}")
            return        
    except sm.ServoInfoException as se:
        ServiceLogger.log_error(__name__, f"{topic}: {se}")
    except sm.ServoInfoException as se:
        ServiceLogger.log_error(__name__, f"{topic}: {se}")

def create_servo_model(section:dict)->sm.Servos2DOF | None:
    try:
        serv =  sm.Servos2DOF(horz_channel=int(section["horz_channel"]), 
                             vert_channel=int(section["vert_channel"]))
        ServiceLogger.log_info(__name__, f"Servo Model created: {serv}")
        
        return serv
    except KeyError as ke:
        ServiceLogger.log_error(__name__, f"Servo Model Key Error: {ke}")
    except ValueError as ve:    
        ServiceLogger.log_error(__name__, f"Servo Model Value Error: {ve}")
    except Exception as e:
        ServiceLogger.log_error(__name__, f"Servo Model Error: {e}")
        
    return None

def create_webservice(section:dict, model:sm.Servos2DOF)->ws.WS_Servo | None:
    try:
        webservice = ws.WS_Servo(uri=section["uri"], 
                                 port=int(section["port"]),
                                 model=model)
        ServiceLogger.log_info(__name__, f"Web Service created: {webservice}")
        
        return webservice
    except KeyError as ke:
        ServiceLogger.log_error(__name__, f"create_webservice, Key Error: {ke}")
    except ValueError as ve:    
        ServiceLogger.log_error(__name__, f"create_webservice, Value Error: {ve}")
    except Exception as e:
        ServiceLogger.log_error(__name__, f"create_webservice, Error: {e}")
    return None

def create_listener(section:dict)->servo_subscriber.Subscriber | None:
    try:
        listener = servo_subscriber.Subscriber(host=section["host"], 
                                               port=int(section["port"]),
                                               user_name=section["username"],
                                               password=section["password"])
        listener.add_callback(servo_subscriber.TopicCallback(f"{topics.SERVO_PREFIX}/{topics.MQTT_WILDCARD}",
                                            handle_servo_message_cb))
        
        ServiceLogger.log_info(__name__, f"Listener created: {listener}")
        
        return listener
    except KeyError as ke:
        ServiceLogger.log_error(__name__, f"create_listener, Key Error: {ke}")
    except ValueError as ve:    
        ServiceLogger.log_error(__name__, f"create_listener, Value Error: {ve}")
    except Exception as e:
        ServiceLogger.log_error(__name__, f"create_listener, Error: {e}")
    return None

def create_async_listener(section:dict)->servo_subscriber.AsyncSubscriber | None:
    try:
        listener = servo_subscriber.AsyncSubscriber(host=section["host"], 
                                               port=int(section["port"]),
                                               user_name=section["username"],
                                               password=section["password"])
        
        ServiceLogger.log_info(__name__, f"Async Listener created: {listener}")        
        return listener
    except KeyError as ke:
        ServiceLogger.log_error(__name__, f"create_async_listener, Key Error: {ke}")
    except ValueError as ve:    
        ServiceLogger.log_error(__name__, f"create_async_listener, Value Error: {ve}")
    except Exception as e:
        ServiceLogger.log_error(__name__, f"create_async_listener, Error: {e}")
    return None

def create_config(config_file:str=CONFIG_FILE)->configparser.ConfigParser | None:
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        ServiceLogger.log_info(__name__, f"Config file read: {config_file}")        
        return config
    except KeyError as ke:
        ServiceLogger.log_error(__name__, f"create_config, Key Error: {ke}")
    except ValueError as ve:    
        ServiceLogger.log_error(__name__, f"create_config, Value Error: {ve}")
    except Exception as e:
        ServiceLogger.log_error(__name__, f"create_config, Error: {e}")
    return None

async def start_tasks():
    global servo_webservice, servo_async_listener, handle_servo_message_cb
    
    ServiceLogger.log_info(__name__, f"Starting Tasks: {servo_webservice}, {servo_async_listener}")
    
    task1 = asyncio.create_task(servo_webservice.update())
    task2 = asyncio.create_task(servo_async_listener.start(
                                                    topic=f"{topics.SERVO_PREFIX}/{topics.MQTT_WILDCARD}",
                                                    callback=handle_servo_message_cb))

    await asyncio.gather(task2, task1)
    # await asyncio.gather(task1)


def main():
    ServiceLogger.log_info(__name__, "Starting Servo Controller")
    global config, servo_model, servo_listener, servo_webservice, servo_async_listener
    
    config = create_config(CONFIG_FILE)
    if config is None:
        ServiceLogger.log_error(__name__, "Error creating Config")
        exit(1)
    
    # Create the servo model
    servo_model = create_servo_model(config["Servos"])
    ServiceLogger.log_info(__name__, f"Servo Model: {id(servo_model)}")    
    if servo_model is None:
        ServiceLogger.log_error(__name__, "Error creating Servo Model")
        exit(1)        
    # create the webservice
    servo_webservice = create_webservice(config["WS_SERVO"], servo_model)
    if servo_webservice is None:
        ServiceLogger.log_error(__name__, "Error creating Web Service")
        exit(1)
        
    # Create the listener
    # servo_listener = create_listener(config["MQTT"])    
    # if servo_listener is None:
    #     ServiceLogger.log_error(__name__, "Error creating Listener")
    #     exit(1)
    
    servo_async_listener = create_async_listener(config["MQTT"])
    if servo_async_listener is None:
        ServiceLogger.log_error(__name__, "Error creating Async Listener")
        exit(1)
      
    asyncio.run(start_tasks())
    

if __name__ == "__main__":
    if not ServiceLogger.is_initialized():
        ServiceLogger.init_logger()
    main()    
