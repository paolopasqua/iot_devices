import time
import board
import adafruit_dht
from smart_sensors_utility import LoggerUtility, ModbusUtility

from pymodbus.server.asynchronous import StartTcpServer

from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import (ModbusRtuFramer,
                                  ModbusAsciiFramer,
                                  ModbusBinaryFramer)


class ModbusDHTDataBlock(ModbusSequentialDataBlock):
    ''' Creates a modbus datastore to get data from DHTXX devices '''

    def __init__(self, dhtDevice, logger):
        ''' Initializes the datastore

        :param dhtDevice: The device instance
        '''
        super().__init__(1, [0]*2)
        self.device = dhtDevice
        self.logger = logger

    def getValues(self, address, count=1):
        ''' Returns the requested values of the datastore

        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        '''
        values = []
        if address == 1:
            act_len = len(values)
            while act_len >= len(values):
                try:
                    values.append(self.device.temperature)
                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    self.logger.error("[temperature]: %s" % error.args[0])
                    continue
                except Exception as error:
                    self.device.exit()
                    self.logger.error("Exiting after exception [temperature]: %s" % error)
                    raise error
        
        if address == 2 or count > 1:
            act_len = len(values)
            while act_len >= len(values):
                try:
                    values.append(self.device.humidity)
                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    self.logger.error("[humidity]: %s" % error.args[0])
                    continue
                except Exception as error:
                    self.device.exit()
                    self.logger.error("Exiting after exception [humidity]: %s" % error)
                    raise error
        
        return values

    def setValues(self, address, values):
        pass

def main():

    log = LoggerUtility.get_logger("dht11.log")

    log.info("**************************** START ****************************")

    # Initial the dht device, with data pin connected to:
    log.info("Initializing the device DHT11 on pin 18...")
    dhtDevice = adafruit_dht.DHT11(board.D18)

    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- # 
    log.info("Setting up data block and context...")
    block = ModbusDHTDataBlock(dhtDevice, log)
    # block = ModbusSequentialDataBlock(0, [3]*5)
    # print(block.getValues(0,2))
    store = {
        0x01: ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    }
    context = ModbusServerContext(slaves=store, single=False)

    # ----------------------------------------------------------------------- # 
    # initialize the server information
    # ----------------------------------------------------------------------- # 
    log.info("Getting identity...")
    identity = ModbusUtility.get_modbus_device_identification("DHT11 Server")

    # ----------------------------------------------------------------------- # 
    # run the TCP Server
    # ----------------------------------------------------------------------- # 
    log.info("Starting TCP Server...")
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 5000))


if __name__ == "__main__":
    main()


# time_delta = 30
# tag = "test"
# sql = "INSERT INTO `dht11` (`tag`, `temperature`, `humidity`) VALUES (%s, %s, %s)"
    
# # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# # This may be necessary on a Linux single board computer like the Raspberry Pi,
# # but it will not work in CircuitPython.
# # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

# log.info("Start collecting data...")
# while True:
#     try:
#         temperature_c = dhtDevice.temperature
#         humidity = dhtDevice.humidity

#         try:
#             log.debug("Data: temp: %.2f °C  ;  humidity: %.2f " % (temperature_c, humidity))
#             with connection.cursor() as cursor:
#                 # Create a new record
#                 log.debug("Executing query: %s" % (sql % (tag,temperature_c,humidity)))
#                 cursor.execute(sql, (tag,temperature_c,humidity))
#             # connection is not autocommit by default. So you must commit to save your changes.
#             connection.commit()
#         except Exception as e:
#             log.error("Exception: %s\nOn executin query: %s" % (e,(sql % (tag,temperature_c,humidity))) )

#     except RuntimeError as error:
#         # Errors happen fairly often, DHT's are hard to read, just keep going
#         log.error(error.args[0])
#         continue
#     except Exception as error:
#         dhtDevice.exit()
#         log.error("Exiting after exception: %s" % error)
#         raise error
    
#     #read pause
#     time.sleep(time_delta)