#actuator.py
from ..device import sOPCUA_Device


class sOPCUA_Actuator(sOPCUA_Device):
    """
        Abstract class to manage an actuator into an OPCUA server
    """

    STATE_OFF = "Off"
    STATE_ON = "On"
    
    KEY_TURN_ON = 'turn_on'
    KEY_TURN_OFF = 'turn_off'

    sOPCUA_Device.class_init({},
                             {KEY_TURN_ON:{'input':[],'output':[]},
                              KEY_TURN_OFF:{'input':[],'output':[]}
                             })


    def __init__(self, category, tag):
        """
            Constructor.

            Args
            ----
            category    string identifier for the category of the actuator

            tag      string identifier for the actuator
        """
        super().__init__(category, tag)
        self.state = self.STATE_OFF

        self.turn_on.connect(lambda n,p=None: setattr(self,'state',self.STATE_ON))
        self.turn_off.connect(lambda n,p=None: setattr(self,'state',self.STATE_OFF))

