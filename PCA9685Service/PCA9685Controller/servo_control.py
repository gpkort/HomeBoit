import time
from adafruit_servokit import ServoKit

NUMBER_OF_SERVOS = 16
DEFAULT_I2C_ADDRESS = 0x40
DEFAULT_FREQUENCY = 50
TIME_DELAY = 0.2

class ServoException(Exception):
    def __init__(self, message:str):
        self.__message = message
        
    @property
    def message(self)->str:
        return self.__message


class ServoControllerPCA9685:
    def __init__(self, 
                 board_address=DEFAULT_I2C_ADDRESS, 
                 frequency=DEFAULT_FREQUENCY):
        self.__kit:ServoKit = ServoKit(channels=NUMBER_OF_SERVOS, address=board_address)
        self.__kit.frequency = frequency        
    
    def update_servo_position(self, channel:int, angle:int)->None:
        if channel < 0 or channel >= NUMBER_OF_SERVOS:
            raise ServoException(f"Invalid Servo Channel: {channel}")
        
        self.__kit.servo[channel].angle = angle
    