#device.py
from abc import ABC, abstractmethod
from ..utils import DynamicMethod, DynamicAttribute
from opcua import ua, uamethod

class sOPCUA_Device(ABC):
    '''
    Base class to rapresent a generic OPCUA Device.
    This object contains the state property and multi server connection.
    '''


    ''' Key value to identify the STATE attribute '''
    KEY_STATE = 'state'
    
    __attributes = None
    __methods = None
    
    def __init__(self, category: str, tag: str, attributes: "Dict[str,ua.VariantType]", methods: "Dict[str,Dict['input':List[ua.Argument],'output':List[ua.Argument],'action':callable]]"):
        """
        Constructor.

        Args
        ----
        category:    string to identify the device category

        tag:         string to identify the device
        """
        self.__class_init__(attributes,methods)

        self.__state = None
        self.__tag = tag
        self.__name = "%s_%s" % (category, self.__tag)
        self.__servers = {}
        super().__init__()

    @property
    def tag(self):
        return self.__tag

    @property
    def name(self):
        return self.__name

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state
        self.call_servers_attribute_method(sOPCUA_Device.KEY_STATE, 'set_value', state)
    
    def get_servers(self):
        '''
        Return the servers list
        '''
        return self.__servers

    def get_server(self, idx):
        '''
        Return the server

        Args
        ----
        idx     server namespace identifier
        '''
        if idx not in self.__servers:
            self.__servers[idx] = {}
        return self.__servers[idx]
    
    def call_servers_attribute_method(self, attr, method, *args, **kwargs):
        '''
        Call an attribute's method with the args and kwargs

        Args
        ----
        attr    attribute name
        method  method name
        args    args to the method
        kwargs  args to the method
        '''
        [getattr(s[attr], method)(*args, **kwargs) for s in self.__servers.values()]
    
    def register_to_server(self, idx, objects_node):
        '''
        Registers device to the server

        Args
        -----
        idx     server identifier

        objects_node    destination node of the object
        '''
        opcua_object = objects_node.add_object(idx, self.name)
        
        self.get_server(idx)[sOPCUA_Device.KEY_STATE] = opcua_object.add_property(idx, sOPCUA_Device.KEY_STATE, self.state, ua.VariantType.String)

        for a in self.__attributes:
            self.get_server(idx)[a] = opcua_object.add_property(idx, a, getattr(self,a), self.__attributes[a].variant_type)
        
        for m in self.__methods:
            opcua_object.add_method(idx, m, getattr(self,m), self.__methods[m].input_par, self.__methods[m].output_par)
    
    def __class_init__(self, attributes: "Dict[str,ua.VariantType]", methods: "Dict[str,Dict['input':List[ua.Argument],'output':List[ua.Argument],'action':callable]]"):
        '''
        Inits the class with the attributes and methods.
        '''
        if not self.__class__.__attributes:
            self.__class__.__attributes = {}
            for a in attributes:
                self.__class__.__attributes[a] = DynamicAttribute(a, attributes[a])
                self.__class__.__attributes[a].delete.connect(self.__class__.__remove_attribute__)
                self.__class__.__attributes[a].set_value.connect(self.__class__.__set_attribute_value__)
                setattr(self.__class__,a,property(self.__class__.__attributes[a].get_value,self.__class__.__attributes[a].set_value,self.__class__.__attributes[a].delete,a))
        
        if not self.__class__.__methods:
            self.__class__.__methods = {}
            for m in methods:
                self.__class__.__methods[m] = DynamicMethod(str(__class__), m, methods[m]['input'], methods[m]['output'])
                self.__class__.__methods[m].delete.connect(self.__class__.__remove_method__)
                if 'action' in methods[m] and callable(methods[m]['action']):
                    self.__class__.__methods[m].connect(methods[m]['action'])
                setattr(self.__class__,m,property(self.__class__.__methods[m].get,None,self.__class__.__methods[m].delete,m))

    @staticmethod
    def __set_attribute_value__(attr: str, instance: "instance reference", value: "dynamic type"):
        '''
        Updates with the value param all the components identified by attr param to instance's servers

        Args
        ----
        attr    attribute name

        instance    reference to instance

        value   value to set
        '''
        instance.call_servers_attribute_method(attr, 'set_value', value)
    
    @staticmethod
    def __remove_attribute__(attribute, instance):
        '''
        Removes the attribute identified by name in instance
        '''
        if attribute in instance.__attributes:
            delattr(instance.__class__,attribute)
            instance.__attributes.pop(attribute)

    @staticmethod
    def __remove_method__(method, instance):
        '''
        Removes the method identified by name in instance
        '''
        if method in instance.__methods:
            delattr(self.__class__,method)
            instance.__methods.pop(method)