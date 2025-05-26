from ServoModel.servo_model import Orientation, ServoInfoException
import json


class ServoData:
    def __init__(self, *, orientation:Orientation, angle:int):
        self.orientation = orientation
        self.angle = angle
        
    def __str__(self):  
        return f"ServoData: {self.orientation.name} {self.angle}"
    
    def to_json_string(self)->str:
        return json.dumps(self.__dict__)    
    
    @staticmethod
    def from_json(json_str:str)->'ServoData':
        try:
            data_dict = json.loads(json_str)
            orient = Orientation.UNKNOWN
            
            if data_dict["orientation"] == "HORZ":
                orient = Orientation.HORZ
            elif data_dict["orientation"] == "VERT":  
                orient = Orientation.VERT
                
            return ServoData(orientation=orient, angle=data_dict["angle"])
        except json.JSONDecodeError as je:
            raise ValueError(f"Error decoding json string: {je.msg}")
        except KeyError as ke:
            raise ValueError(f"Key Error: {ke}")
        except Exception as e:
            raise ValueError(f"Error: {e}")
        
    @staticmethod
    def from_json_bytes(json_bytes:bytes)->'ServoData':
        try:
            return ServoData.from_json(json_bytes.decode())
        except Exception as e:
            raise ServoInfoException(f"Json loading form bytes Error: {e}")


MQTT_WILDCARD = "#"

SERVO_PREFIX: str = "servo"
INCREMENT: str = f"{SERVO_PREFIX}/increment"
DECREMENT: str = f"{SERVO_PREFIX}/decrement"
SET: str = f"{SERVO_PREFIX}/set"

