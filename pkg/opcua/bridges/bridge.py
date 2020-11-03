from .. import OPCUA_Device
from abc import ABC, abstractmethod

class OPCUA_Source:

    def __init__(self, server_address: str, ):
        pass

class OPCUA_Bridge(ABC):
    """
        Abstract class to connect two or more devices.
    """

    def __init__(self, sources: "list of OPCUA_Device" = None, destinations: "list of OPCUA_Device" = None, source_type = OPCUA_Device, destination_type = OPCUA_Device):
        
        if sources:
            self.__sources = sources if sources is list else [sources]
        else:
            self.__sources = []
        for s in self.__sources:
            if isinstance(s, source_type):
                raise TypeError("Invalid type for source: %s" % str(s))
        
        if destinations:
            self.__dests = destinations if destinations is list else [destinations]
        else:
            self.__dests = []
        for d in self.__dests:
            if isinstance(d, destination_type):
                raise TypeError("Invalid type for destination: %s" % str(d))

    def get_sources(self) -> "list of OPCUA_Device":
        """
            Return the sources.
        """
        return self.__sources

    def get_destinations(self) -> "list of OPCUA_Device":
        """
            Return the destinations.
        """
        return self.__dests

    def validate(self):
        """
            Method to valide the bridge condition on the sources. 
        """
        return True

    @abstractmethod
    def do_action(self):
        """
            Method to do the action on bridge destinations.
        """
        pass