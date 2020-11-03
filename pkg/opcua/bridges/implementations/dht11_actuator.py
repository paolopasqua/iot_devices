from ..bridge import OPCUA_Bridge
from ...actuators import OPCUA_Actuator
from ...sensors import OPCUA_DHT_Sensor

class OPCUA_DHT11_Over_Actuator(OPCUA_Bridge):
    
    def __init__(self, sources: "list of OPCUA_DHT_Sensor", destinations: "list of OPCUA_Actuator"):
        super().__init__(sources=sources, destinations=destinations, source_type=OPCUA_DHT_Sensor, destination_type=OPCUA_Actuator)
    
    def validate(self):
        if super().validate():
            for s in self.get_sources():
                

    
    def do_action(self):
        return super().do_action()