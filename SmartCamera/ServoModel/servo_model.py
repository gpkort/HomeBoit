from dataclasses import dataclass
from enum import Enum

class ServoInfoException(Exception):
    def __init__(self, message:str):
        self.__message = message
        
    @property
    def message(self)->str:
        return self.__message

class Orientation(Enum):
    HORZ = 1
    VERT = 2
    UNKNOWN = 3
    

class Servo:
    SERVO_MAX = 180
    SERVO_MIN = 0
        
    def __init__(self, channel:int=-1, angle:int=0, is_dirty:bool=False):
        self.__channel:int = channel
        self.__angle:int = angle 
        self.is_dirty:bool = is_dirty       
    
    @property   
    def channel(self)->int:
        return self.__channel
    
    @property
    def angle(self)->int:
        return self.__angle
    
    def increment_angle(self, amount:int)->None:
        self.set_angle(self.__angle + amount)
        
    def decrement_angle(self, amount:int)->None:
        self.set_angle(self.__angle - amount)
    
    def set_angle(self, angle:int)->None:
        self.__angle = Servo.get_valid_servo_angle(angle) 
        self.is_dirty = True
               
    def __str__(self):
        return f"Servo: Channel: {self.__channel} Position: {self.__angle}, Dirty: {self.is_dirty}"
    
    def to_json_string(self)->str:
        ret_val = "{"
        ret_val += f"\"channel\":{self.__channel},"
        ret_val += f"\"angle\":{self.__angle}"
        ret_val += "}"
        return ret_val
    
    @staticmethod
    def from_json(json:dict)->'Servo':
        try:
            channel = json.get("channel", -1)
            angle = json["angle"]
            return Servo(channel, angle)        
        except KeyError as ke:
            raise ServoInfoException(f"Key Error: {ke}")
        except ValueError as ve:
            raise ServoInfoException(f"Value Error: {ve}")
        except Exception as e:          
            raise ServoInfoException(f"Error: {e}")
   
       
    @staticmethod
    def from_json_bytes(json:bytes)->'Servo':
        try:
            return Servo.from_json(json.loads(json))
        except ServoInfoException as sie:
            raise sie
        except Exception as e:
            raise ServoInfoException(f"Json loading from bytes Error: {e}")
    
    @staticmethod
    def get_valid_servo_angle(angle:int)->int:
        if angle < Servo.SERVO_MIN:
            return Servo.SERVO_MIN
        elif angle > Servo.SERVO_MAX:
            return Servo.SERVO_MAX
        return angle
   
class Servos2DOF:
    def __init__(self, *, horz_channel:int, vert_channel:int):
        self.servos:dict[Orientation, Servo] = {
            Orientation.HORZ: Servo(horz_channel, 0),
            Orientation.VERT: Servo(vert_channel, 0)
        }
        
    def increment_servo_angle(self, orientation:Orientation, angle:int)->bool:
        if orientation == Orientation.UNKNOWN:
            raise ServoInfoException("Unknown servo orientation in increment_servo_angle")
        self.servos[orientation].increment_angle(angle)
    
    def decrement_servo_angle(self, orientation:Orientation, angle:int)->bool:
        if orientation == Orientation.UNKNOWN:
            raise ServoInfoException("Unknown servo orientation in decrement_servo_angle")
        self.servos[orientation].decrement_angle(angle)
        
    def set_servo_angle(self, orientation:Orientation, angle:int)->bool:
        if orientation == Orientation.UNKNOWN:
            raise ServoInfoException("Unknown servo orientation in set_servo_angle")
        self.servos[orientation].set_angle(angle)
    
    def get_servo_angle(self, orientation:Orientation)->int:    
        if orientation == Orientation.UNKNOWN:
            raise ServoInfoException("Unknown servo orientation in get_servo_angle")
        return self.servos[orientation].angle    
    
    @property
    def horz_servo(self)->Servo:
        return self.servos[Orientation.HORZ]
    
    @property   
    def vert_servo(self)->Servo:
        return self.servos[Orientation.VERT]
            
        
    def to_json_string(self)->str:
        ret = "{"
        ret += f"\"HORZ\":{self.servos[Orientation.HORZ].to_json_string()},"
        ret += f"\"VERT\":{self.servos[Orientation.VERT].to_json_string()}"
        ret += "}"
    
    @staticmethod
    def from_json(json:list[dict])->'Servos2DOF':
        servos = Servos2DOF(json["HORZ"]["channel"], json["VERT"]["channel"])
    
    def __str__(self):
        retval = "Servos2DOF: "
        retval += f"Horz: {self.servos[Orientation.HORZ]} "
        retval += f"Vert: {self.servos[Orientation.VERT]}"
        return retval
 
    
