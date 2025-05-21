import json
from enum import Enum
from PCA9685Logger.servo_logger import ServiceLogger

class PCA9685Status(Enum):
    OK = 'OK'
    REQUEST_ERROR = 'REQUEST_ERROR'
    BOARD_ERROR = 'BOARD_ERROR'
    
    def __str__(self):
        return self.name
    
class PCA9685Command(Enum):
    SET_ANGLE = 'SET_ANGLE'
    GET_ANGLE = 'GET_ANGLE'
    HELLO = 'HELLO'
    
    def __str__(self):
        return self.name
    
class PCA9685MessageException(Exception):
    def __init__(self, message):
        self.__message = message  
    @property
    def message(self)->str:
        return self.__message

class ServoInfoJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__
 
class ServoInfo:
    def __init__(self, channel:int, angle:int):
        self.channel:int = channel
        self.angle:int = angle
        
    def __str__(self):
        return f'Channel: {self.channel}, Angle: {self.angle}'
    
    def __dict__(self):
        return {'channel': self.channel, 'angle': self.angle}
    
    def to_json(self)->str:
        return json.dumps(self, cls=ServoInfoJSONEncoder)
    
    @staticmethod
    def from_json(json_str:str)->'ServoInfo' :
        try:
            obj = json.loads(json_str)
            return ServoInfo(obj['channel'], obj['angle'])
        except json.JSONDecodeError as e:
            raise PCA9685MessageException(f'Servo Info Invalid JSON - {e.msg}, {e.doc}, ln {e.lineno}')
        except KeyError as e:
            raise PCA9685MessageException(f'Servo Info Missing JSON Key - {e}')
        except ValueError as e:
            raise PCA9685MessageException(f'Servo Info Invalid JSON Value- {e}')   
        except Exception as e:
            raise PCA9685MessageException(f'Servo Info Invalid JSON General Exception- {e}')

class PCA9685RequestJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__    
    
class PCA9685Request:
    def __init__(self, command:PCA9685Command, servo:ServoInfo=None):
        self.command:PCA9685Command = command
        self.servo:ServoInfo = servo       
    
    def __str__(self):
        return f'Command: {self.command}, Servo: {self.servo}'
    
    def __dict__(self):
        return {'command': self.command, 'servo': self.servo}
    
    def to_json(self)->str:
        return json.dumps(self, cls=PCA9685RequestJSONEncoder)
    
    @staticmethod
    def from_json(json_str:str)->'PCA9685Request' :
        try:
            temp = json.loads(json_str)
            return PCA9685Request(PCA9685Command(temp['command']), 
                                  ServoInfo(temp['servo']['channel'], 
                                            temp['servo']['angle']))
        except json.JSONDecodeError as e:
            raise PCA9685MessageException(f'Request Invalid JSON - {e.msg}, {e.doc}, ln {e.lineno}')
        except KeyError as e:
            raise PCA9685MessageException(f'Request Missing JSON Key - {e}')
        except ValueError as e:
            raise PCA9685MessageException(f'Request Invalid JSON Value- {e}')   
        except Exception as e:
            raise PCA9685MessageException(f'Request Invalid JSON General Exception- {e}')

class PCA9685ReplyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class PCA9685Reply:
    def __init__(self, status:PCA9685Status, message:str=""):
        self.status:PCA9685Status = status
        self.message:str = message
    
    def __str__(self):
        return f'Status: {self.status}, Message: {self.message}'     
    
    def __dict__(self):
        return {'status': self.status, 'message': self.message}  
    
    def to_json(self)->str:
        return json.dumps(self, cls=PCA9685ReplyJSONEncoder)
    
    @staticmethod   
    def from_json(json_str:str)->'PCA9685Reply' :
        try:
            obj = json.loads(json_str)            
            return PCA9685Request(status=PCA9685Status[obj['status']], message=obj['message'])
        except json.JSONDecodeError as e:
            raise PCA9685MessageException(f'Reply Invalid JSON - {e.msg}, {e.doc}, ln {e.lineno}')
        except KeyError as e:
            raise PCA9685MessageException(f'Reply Missing JSON Key - {e}')
        except ValueError as e:
            raise PCA9685MessageException(f'Reply Invalid JSON Value- {e}')   
        except Exception as e:
            raise PCA9685MessageException(f'Reply Invalid JSON General Exception- {e}')
    