#relay.py
from .actuator import sOPCUA_Actuator
import RPi.GPIO as GPIO
import logging

class sOPCUA_Relay(sOPCUA_Actuator):
    """
        Class to manage a RELAY actuator into an OPCUA server
    """
    def __init__(self, pin, tag):
        logging.debug("INIT %s(%s,%s) into %s" % (__class__,pin,tag,self))
        super().__init__("RELAY", tag)
        self.__pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.__pin, GPIO.OUT)
        GPIO.output(self.__pin, GPIO.LOW)

        self.turn_on.connect(self.__turn_on__)
        self.turn_off.connect(self.__turn_off__)
        
    
    def __turn_on__(self, parent, ua_parent):
        logging.debug("RELAY[%s] turning on" % self)
        GPIO.output(self.__pin, GPIO.HIGH)

    def __turn_off__(self, parent, ua_parent):
        logging.debug("RELAY[%s] turning off" % self)
        GPIO.output(self.__pin, GPIO.LOW)
