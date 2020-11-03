
from .actuator import OPCUA_Actuator
import RPi.GPIO as GPIO

class OPCUA_Relay_Actuator(OPCUA_Actuator):
    """
        Class to manage a RELAY actuator into an OPCUA server
    """
    def __init__(self, pin, tag):
        super().__init__("RELAY", tag)
        self.__pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin, GPIO.OUT)
        GPIO.output(self.__pin, GPIO.LOW)

    def build_object(self, idx, opcua_object):
        super().build_object(idx, opcua_object)
    
    def __turn_on__(self, parent):
        super().__turn_on__(parent)
        GPIO.output(self.__pin, GPIO.HIGH)

    def __turn_off__(self, parent):
        super().__turn_off__(parent)
        GPIO.output(self.__pin, GPIO.LOW)
