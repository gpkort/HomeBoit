import asyncio
import websockets

from ServoModel.servo_model import Servos2DOF, Servo
from ServoLogger.servo_logger import ServiceLogger

class WS_Servo:
    WS_COMMAND:str = "SET_ANGLE"
    WS_HELLO:str = "HELLO"
    
    def __init__(self, uri:str, port:int, model:Servos2DOF):
        self.__uri = uri
        self.__port = port
        self.__model = model


    async def update(self):
        global ServiceLogger
        ServiceLogger.log_info(__name__, "WS_Servo.update")
        uri = f"ws://{self.__uri}:{self.__port}"
        
        async with websockets.connect(uri) as websocket:
            while True:
                command: str = WS_Servo.WS_HELLO
                servo_mod: Servo = Servo(-1, -1)
                        
                for val in self.__model.servos.values(): 
                    if val.is_dirty:
                        command = WS_Servo.WS_COMMAND
                        servo_mod = val
                
                command_str: str = "{"
                command_str += f"\"command\":\"{command}\", "
                command_str += f"\"servo\":{servo_mod.to_json_string()}"
                command_str += "}"
                            
                await websocket.send(command_str)
                if command == WS_Servo.WS_COMMAND:
                    ServiceLogger.log_info(__name__, f"Sent: {command_str} to {uri}")
                    val.is_dirty = False
                status = await websocket.recv()
            
                if "Status: OK" in status: 
                    if command == WS_Servo.WS_COMMAND:
                        val.is_dirty = False
                        ServiceLogger.log_info(__name__, f"Received: {status} from {uri}")
                else:
                    ServiceLogger.log_error(__name__, f"Received: {status} from {uri}")
    def run(self):
        asyncio.run(self.update())        

