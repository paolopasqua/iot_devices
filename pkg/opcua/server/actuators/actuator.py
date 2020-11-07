#actuator.py
from ..device import sOPCUA_Device


class sOPCUA_Actuator(sOPCUA_Device):
    """
        Abstract class to manage an actuator into an OPCUA server
    """

    STATE_OFF = "Off"
    STATE_ON = "On"
    
    MKEY_TURN_ON = 'turn_on'
    MKEY_TURN_OFF = 'turn_off'

    # class_init({},
    #                          {MKEY_TURN_ON:{'input':[],'output':[]},
    #                           MKEY_TURN_OFF:{'input':[],'output':[]}
    #                          })


    def __init__(self, category, tag):
        """
            Constructor.

            Args
            ----
            category    string identifier for the category of the actuator

            tag      string identifier for the actuator
        """
        super().__init__(
                        category, 
                        tag, 
                        {},
                        {
                            self.MKEY_TURN_ON:{'input':[],'output':[]},
                            self.MKEY_TURN_OFF:{'input':[],'output':[]}
                        })
        self.state = self.STATE_OFF

        self.turn_on.connect(lambda n,p=None: setattr(self,sOPCUA_Device.KEY_STATE,self.STATE_ON))
        self.turn_off.connect(lambda n,p=None: setattr(self,sOPCUA_Device.KEY_STATE,self.STATE_OFF))

