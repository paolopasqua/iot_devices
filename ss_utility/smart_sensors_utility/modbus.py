
from pymodbus.device import ModbusDeviceIdentification

class ModbusUtility(object):

    def get_modbus_device_identification(model_name):
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'paoloapasqua'
        identity.ProductCode = 'SS'
        identity.VendorUrl = 'https://github.com/paolopasqua'
        identity.ProductName = 'SmartSensors'
        identity.ModelName = model_name
        identity.MajorMinorRevision = '0.0.1'

        return identity