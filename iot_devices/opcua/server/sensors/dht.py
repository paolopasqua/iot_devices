from ..device import sOPCUA_Device
from opcua import ua, uamethod
from abc import ABC
import adafruit_dht
import threading
import logging
import board
import time

def get_update_refresh_time_input():
    input_arg = ua.Argument()
    input_arg.Name = "seconds"
    input_arg.DataType = ua.NodeId(ua.VariantType.Int64.value)
    return [input_arg]

def get_update_refresh_time_output():
    output_arg = ua.Argument()
    output_arg.Name = "result"
    output_arg.DataType = ua.NodeId(ua.VariantType.Boolean.value)
    return [output_arg]


class sOPCUA_DHT(sOPCUA_Device):
    """
        Class to manage a DHT sensor into an OPCUA server.
    """
    
    DHT11 = "DHT11"
    DHT22 = "DHT22"

    KEY_REFRESH_TIME = 'refresh_time'
    KEY_TEMPERATURE = 'temperature'
    KEY_HUMIDITY = 'humidity'
    MKEY_UPDATE_REFRESH_TIME = 'update_refresh_time'
    MKEY_START = 'start'
    MKEY_FREEZE = 'freeze'

    STATE_FREEZED = "Freezed"
    STATE_RUNNING = "Running"
    STATE_READING = "Reading"

    def __init__(self, model: "DHT11/DHT22 constants", tag: str, pin: "board constants in str"):
        """
            Constructor.

            Args
            ----
            model:    DHT11 or DHT22 constants: the model of the device

            tag:      string with the identifier tag of the device

            pin:      board library constants: the pin of the board used for data
        """
        logging.debug("INIT %s(%s,%s,%s) into %s" % (__class__,model,tag,pin,self))
        super().__init__(
                        model, 
                        tag,
                        {
                            self.KEY_TEMPERATURE:ua.VariantType.Int64,
                            self.KEY_HUMIDITY:ua.VariantType.Int64,
                            self.KEY_REFRESH_TIME:ua.VariantType.Int64
                        },
                        {
                            self.MKEY_START:{'input':[],'output':[]},
                            self.MKEY_FREEZE:{'input':[],'output':[]},
                            self.MKEY_UPDATE_REFRESH_TIME:{'input':get_update_refresh_time_input(),'output':get_update_refresh_time_output()}
                        })
        self.device = getattr(adafruit_dht,model)(getattr(board, pin))
        self.state = self.STATE_FREEZED

        self.temperature = 0
        self.humidity = 0
        self.refresh_time = 1

        self.start.connect(self.__start__)
        self.freeze.connect(self.__freeze__)
        self.update_refresh_time.connect(self.__update_refresh_time__)

        self.timing_cond = threading.Condition()
        self.updater = threading.Thread(name=self.name, target=self.__thread_job__, args=(self.timing_cond,))
        self.freeze_state = False

    def __del__(self):
        if getattr(self,'device',None):
            self.device.exit()
            self.device = None
        super().__del__()

    def __start__(self, parent, ua_parent):
        """
            Start the reading data thread. This method is called even from OPCUA clients.
        """
        self.freeze_state = False
        self.updater.start()

    def __freeze__(self, parent, ua_parent):
        """
            Stop the reading data thread. This method is called even from OPCUA clients.
        """
        self.freeze_state = True
        with self.timing_cond:
            self.timing_cond.notify()

    def __update_refresh_time__(self, parent, ua_parent, seconds):
        """
            Updates the refresh time of reading data and notify change to servers.
        """
        try:
            logging.debug("DHT[%s] updating refresh time" % self)
            self.refresh_time = seconds.Value
            with self.timing_cond:
                self.timing_cond.notify()
            return True
        except Exception as error:
            logging.error("DHT[%s] %s" % (self,error))
            return False

    def __thread_job__(self, timing_cond):
        """
            Thread job routine to read updated data from sensor.

            @param timing_cond  condition to control the execution
        """
        logging.debug("DHT[%s] started" % self)
        self.state = self.STATE_RUNNING

        while not self.freeze_state:
            self.__update_data__()
            self.state = self.STATE_RUNNING
            with timing_cond:
                logging.debug("DHT[%s] waiting" % self)
                timing_cond.wait(self.refresh_time)

        logging.debug("DHT[%s] stopped" % self)
        self.state = self.STATE_FREEZED

    def __update_data__(self):
        """
            Read updated data from sensor and update value to OPCUA servers.
        """
        logging.debug("DHT[%s] starting reading" % self)
        self.state = self.STATE_READING
        read = False
        while not read:
            try:
                self.temperature = self.device.temperature
                self.humidity = self.device.humidity
                logging.debug("DHT[%s] readed temp: %d ; hum: %d" % (self,self.temperature,self.humidity))
                read = True
            except Exception as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                logging.error("DHT[%s] %s" % (self,error))
                read = False