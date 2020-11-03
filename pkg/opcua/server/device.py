from abc import ABC, abstractmethod
# from opcua import ua, uamethod


class DynamicMethod():
    '''
    Class to manage a dynamic method. It can connect to external methods and call them when it is called.

    All the connected method must have the same parameters.
    '''

    def __init__(self):
        self.__methods = []

    def connect(self, method: "callable"):
        '''
        Connect a method
        '''
        if callable(method):
            self.__methods.append(method)
    
    def __call__(self, *args, **kwargs):
        for m in self.__methods:
            m(*args, **kwargs)


class sOPCUA_Device(ABC):
    '''
    Base class to rapresent a generic OPCUA Device.
    This object contains the state property and multi server connection.
    '''

    KEY_STATE = 'state'

    def __init__(self, category: str, tag: str, attributes: "Dict[str,ua.VariantType]", methods: "Dict[str,Dict['input':List[ua.Argument],'output':List[ua.Argument]]]"):
        """
        Constructor.

        Args
        ----
        category:    string to identify the device category

        tag:         string to identify the device
        
        attributes:  dictionary with the attribute name as key and the type as value
        """
        self.__state = None
        self.__tag = tag
        self.__name = "%s_%s" % (category, self.__tag)
        self.__servers = {}
        self.__attributes = {}
        self.__methods = {}
        super().__init__()

        setattr(self.__class__,'tag',property(lambda s: s.__get_tag__(),None,None,'tag'))
        setattr(self.__class__,'name',property(lambda s: s.__get_name__(),None,None,'name'))
        setattr(self.__class__,'state',property(lambda s: s.__get_state__(),lambda s,v: s.__set_state__(v),None,'state'))

        for a in attributes:
            self.__attributes[a] = {}
            self.__attributes[a]['type'] = attributes[a]
            self.__attributes[a]['value'] = None
            # setattr(self,'get_'+a,lambda: self.__attributes[a]['value'])
            # setattr(self,'set_'+a,lambda value: self.__set_attribute_value__(a,value))
            setattr(self.__class__,a,property(lambda s: s.__attributes[a]['value'],lambda s, value: s.__set_attribute_value__(a,value),lambda s: s.__attributes.pop(a),a))
        
        for m in methods:
            self.__methods[m] = {}
            self.__methods[m]['method'] = DynamicMethod()
            self.__methods[m]['input'] = methods[m]['input']
            self.__methods[m]['output'] = methods[m]['output']
            setattr(self.__class__,m,property(lambda s: s.__methods[m]['method'],None,lambda s: s.__methods.remove(m) if m in s.__methods else None,m))

    def __set_attribute_value__(self, attr: str, value: "dynamic type"):
        '''
        Update with the value param all the components identified by attr param to servers

        Args
        ----
        attr    attribute name
        value   value to set
        '''
        # [s[attr].set_value(value) for s in self.__servers().values()]
        if attr in self.__attributes:
            self.__attributes[attr]['value'] = value
        else:
            raise AttributeError("Invalid attribute name: %s" % attr)
        self.call_servers_attribute_method(attr, 'set_value', value)

    def __get_tag__(self):
        return self.__tag

    def __get_name__(self):
        return self.__name

    def __get_state__(self):
        return self.__state

    def __set_state__(self, state):
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
        opcua_object = objects_node.add_object(idx, self.get_name())
        
        self.get_server(idx)[sOPCUA_Device.KEY_STATE] = opcua_object.add_property(idx, sOPCUA_Device.KEY_STATE, self.state, ua.VariantType.String)

        for a in self.__attributes:
            self.get_server(idx)[a] = opcua_object.add_property(idx, a, self.__attributes[a]['value'], self.__attributes[a]['type'])
        
        for m in self.__methods:
            opcua_object.add_method(idx, m, self.__methods[m]['method'], self.__methods[m]['input'], self.__methods[m]['output'])
