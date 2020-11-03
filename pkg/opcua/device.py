from abc import ABC, abstractmethod
from opcua import ua, uamethod
 
class OPCUA_Device(ABC):
    '''
    Base class to rapresent a generic OPCUA Device.
    This object contains the state property and multi server connection.
    '''

    KEY_STATE = 'state'
 
    def __init__(self, device_category, device_tag):
        self.__state = None
        self.__tag = device_tag
        self.__name = "%s_%s" % (device_category, self.__tag)
        self.__servers = {}
        super().__init__()
    
    def get_tag(self):
        return self.__tag

    def get_name(self):
        return self.__name

    def set_state(self, state):
        self.__state = state
        self.update_component_value(OPCUA_Device.KEY_STATE, state)
    
    def get_state(self):
        return self.__state
    
    def get_servers(self):
        return self.__servers

    def get_server(self, idx):
        if idx not in self.__servers:
            self.__servers[idx] = {}
        return self.__servers[idx]
    
    def append_component_to_server(self, idx, key, component):
        '''
        Append the component to the server with the specified key.
        A component is a property or a variable.
        '''
        self.get_server(idx)[key] = component

    def get_component_from_server(self, idx, key):
        '''
        Return the component identified by server idx and key
        '''
        return self.get_server(idx)[key]
    
    def update_component_value(self, key, new_value):
        '''
        Update with the new_value param all the components identified by key param to servers
        '''
        [s[key].set_value(new_value) for s in self.get_servers().values()]

    def append_to_server(self, idx, objects_node):
        '''
        Append to the server idx the object for this instance.

        This method calls the abstract method build_object to allow child classes to add custom properties, variables and methods.

        @param idx server identifier
        @param object_node destination node of the object
        '''
        opcua_object = objects_node.add_object(idx, self.get_name())
        
        self.append_component_to_server(idx, OPCUA_Device.KEY_STATE, opcua_object.add_property(idx, OPCUA_Device.KEY_STATE, self.get_state(), ua.VariantType.String))
        
        self.build_object(idx, opcua_object)

    @abstractmethod
    def build_object(self, idx, opcua_object):
        '''
        Abstract method to implement with the object construction.  
        NB: the state property is already added to object.
        
        @param opcua_object the object to build with properties, variables and methods.
        '''
        pass