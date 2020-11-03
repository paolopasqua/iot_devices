from ..device import OPCUA_Device
from abc import ABC, abstractmethod

# KEY_STATE = OPCUA_Device.KEY_STATE

STATE_OFF = "Off"
STATE_ON = "On"

class OPCUA_Actuator(OPCUA_Device):
    """
        Abstract class to manage an actuator into an OPCUA server
    """
    def __init__(self, category, tag):
        """
            Constructor.

            @param category string identifier for the category of the actuator
            @param tag      string identifier for the actuator
        """
        super().__init__(category, tag)
        self.set_state(STATE_OFF)

    def build_object(self, idx, opcua_object):
        opcua_object.add_method(idx, "turn_on", self.__turn_on__, [], [])
        opcua_object.add_method(idx, "turn_off", self.__turn_off__, [], [])
    
    def turn_on(self):
        """
            Turn on the actuator
        """
        self.__turn_on__(None)

    @abstractmethod
    def __turn_on__(self, parent):
        """
            Abstract method to implement with operations to turning on the actuator
        """
        self.set_state(STATE_ON)
    
    def turn_off(self):
        """
            Turn off the actuator
        """
        self.__turn_off__(None)

    @abstractmethod
    def __turn_off__(self, parent):
        """
            Abstract method to implement with operations to turning off the actuator
        """
        self.set_state(STATE_OFF)
