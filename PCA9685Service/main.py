from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedOK
import asyncio
import configparser 

from PCA9685Logger.servo_logger import ServiceLogger
from PCA9685messages import messages as pmessage
from PCA9685Controller.servo_control import (ServoControllerPCA9685,
                                              ServoException)
from PCA9685messages.messages import (PCA9685Request, 
                                      PCA9685Reply,
                                      PCA9685Command,
                                      PCA9685Status,
                                      PCA9685MessageException)

CONFIG_FILE = "config.ini"

servo_controller:ServoControllerPCA9685 = ServoControllerPCA9685()

async def handle_command(pmessage:PCA9685Request)->PCA9685Reply:
    global servo_controller
    
    if servo_controller is None:
        ServiceLogger.log_error(__name__, 'Servo Controller is not initialized')
    
    try:
        if pmessage.command == PCA9685Command.SET_ANGLE:
            servo_controller.update_servo_position(pmessage.servo.channel, pmessage.servo.angle)
            return PCA9685Reply(PCA9685Status.OK)
        elif pmessage.command == PCA9685Command.HELLO:
            return PCA9685Reply(PCA9685Status.OK, f"Hello from PCA9685Logger")            
        else:
            ServiceLogger.log_error(__name__, f"Command \"{pmessage.command}\" is not supported")
            return PCA9685Reply(PCA9685Status.REQUEST_ERROR, f"Command \"{pmessage.command}\" is not supported")
    except Exception as e:
        ServiceLogger.log_error(__name__, str(e))
        return PCA9685Reply(PCA9685Status.REQUEST_ERROR, str(e))
    
    
async def handler(websocket):  
    while True:
        try:
            message = await websocket.recv()
            
            reply:PCA9685Reply = None
            
            try:
                pmessage = PCA9685Request.from_json(message)
                if pmessage.command == PCA9685Command.GET_ANGLE:
                    ServiceLogger.log_info(__name__, 'Received message: ' + message)
                reply = await handle_command(pmessage)
            except PCA9685MessageException as e:
                ServiceLogger.log_error({__name__}, e.message)
                reply = PCA9685Reply(PCA9685Status.REQUEST_ERROR, e.message)
            
            await websocket.send(f"{str(reply)}") 
        except ConnectionClosedOK:
            ServiceLogger.log_info(__name__, 'Connection closed')
            break


async def main():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    ServiceLogger.init_logger(None, config['LOGGING']['location'])
    # servo_controller = ServoControllerPCA9685()
    
    ServiceLogger.log_info(__name__, 'Starting PCA9685Logger')   
    
    async with serve(handler, "0.0.0.0", 5001):
        await asyncio.get_running_loop().create_future()  # run forever
    
    
if __name__ == "__main__":   
    asyncio.run(main())