#dynamic.py

class DynamicAttribute():
    '''
    Class to manage a dynamic attribute.
    '''
    def __init__(self, name: str, type_: "ua.VariantType", value: "dynamic value type" = None):
        self.__name = name
        self.__type = type_
        self.__value = value
        self.__set_value = DynamicMethod(self.__name,'set_value',['attr_name','instance','value'])
        self.__set_value.connect(self.__set_value__) #implicit method to save the value
        self.__delete = DynamicMethod(self.__name,'delete',[],[])
    
    @property
    def set_value(self):
        '''set_value calls connected method with parameters: (name,instance,value)'''
        return self.__set_value
    
    def __set_value__(self, name, instance, value):
        self.__value = value

    @property
    def delete(self):
        return self.__delete

    @property
    def name(self):
        return __name

    @property
    def variant_type(self):
        return __type
    
    def get_value(self, instace):
        return self.__value

class DynamicMethod():
    '''
    Class to manage a dynamic method. It can connect to external methods and call them when it is called.

    All the connected method must have the same parameters: parent name, in_param.
    '''

    class CallableVariable():
        def __init__(self, parent: str):
            self.__methods = []
            self.__parent = parent
        
        def connect(self, method: "callable"):
            '''
            Connect a method
            '''
            if callable(method):
                self.__methods.append(method)

        def get(self, instance):
            '''
            Return the dynamic method instance ignoring every parameter
            '''
            return self

        def __call__(self, *args, **kwargs):
            for m in self.__methods:
                m(self.__parent, *args, **kwargs)


    def __init__(self, parent: str, method_name: str, in_param: "List[ua.Argument]" = [], out_param: "List[ua.Argument]" = []):
        self.__parent = parent
        self.__name = method_name
        self.__input = in_param
        self.__output = out_param
        self.__callable = DynamicMethod.CallableVariable(self.__parent)
        self.__delete = DynamicMethod.CallableVariable(self.__name)
        # self.__delete.connect(self.__delete__)
        setattr(self.__class__,'delete',property(self.__delete.get,None,None,''))
    
    @property
    def parent(self):
        '''
        Return the name
        '''
        return self.__parent

    @property
    def input_par(self):
        '''
        Return the input parameters
        '''
        return self.__input

    @property
    def output_par(self):
        '''
        Return the output parameters
        '''
        return self.__output

    def connect(self, method: "callable"):
        '''
        Connect a method
        '''
        self.__callable.connect(method)

    def get(self, instance):
        '''
        Return the dynamic method instance ignoring every parameter
        '''
        return self

    # def __delete__(self, name, instance):
    #     delattr(instance.__class__,name)

    def __call__(self, *args, **kwargs):
        self.__callable(*args, **kwargs)