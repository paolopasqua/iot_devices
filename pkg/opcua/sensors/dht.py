from ..device import OPCUA_Device
from opcua import ua, uamethod
from abc import ABC
import adafruit_dht
import threading
import board
import time

KEY_STATE = OPCUA_Device.KEY_STATE
KEY_REFRESH_TIME = 'refresh_time'
KEY_TEMPERATURE = 'temperature'
KEY_HUMIDITY = 'humidity'

STATE_FREEZED = "Freezed"
STATE_RUNNING = "Running"
STATE_READING = "Reading"

class OPCUA_DHT_Sensor(OPCUA_Device):
    """
        Class to manage a DHT sensor into an OPCUA server.
    """
    def __init__(self, device, model: str, tag: str):
        """
            Constructor.

            @param device   adafruit_dht device [DHT11/DHT22]
            @param model    string with the model of the device
            @param tag      string with the identifier tag of the device
        """
        super().__init__(model, tag)
        self.device = device
        self.set_state(STATE_FREEZED)

        self.refresh_time = 1

        self.timing_cond = threading.Condition()
        self.updater = threading.Thread(name=self.get_name(), target=self.__thread_job__, args=(self.timing_cond,))
        self.freeze = False
    
    def build_object(self, idx, opcua_object):
        self.append_component_to_server(idx, KEY_REFRESH_TIME, opcua_object.add_property(idx, KEY_REFRESH_TIME, self.refresh_time, ua.VariantType.Int64))
        self.append_component_to_server(idx, KEY_TEMPERATURE, opcua_object.add_property(idx, KEY_TEMPERATURE, 0.0))
        self.append_component_to_server(idx, KEY_HUMIDITY, opcua_object.add_property(idx, KEY_HUMIDITY, 0.0))

        input_arg = ua.Argument()
        input_arg.Name = "seconds"
        input_arg.DataType = ua.NodeId(ua.VariantType.Int64.value)

        output_arg = ua.Argument()
        output_arg.Name = "result"
        output_arg.DataType = ua.NodeId(ua.VariantType.Boolean.value)

        opcua_object.add_method(idx, "update_refresh_time", self.__update_refresh_time__, [input_arg], [output_arg])
        opcua_object.add_method(idx, "start", self.__start__, [], [])
        opcua_object.add_method(idx, "freeze", self.__freeze__, [], [])
    
    def exit(self):
        """
            Close the device channels
        """
        self.device.exit()

    def start(self):
        """
            Start the reading data thread.
        """
        self.__start__(None)
    
    def freeze(self):
        """
            Stop the reading data thread
        """
        self.__freeze__(None)
    
    @uamethod
    def __start__(self, parent):
        """
            Start the reading data thread. This method is called even from OPCUA clients.
        """
        self.freeze = False
        self.updater.start()

    @uamethod
    def __freeze__(self, parent):
        """
            Stop the reading data thread. This method is called even from OPCUA clients.
        """
        self.freeze = True
        with self.timing_cond:
            self.timing_cond.notify()

    def __thread_job__(self, timing_cond):
        """
            Thread job routine to read updated data from sensor.

            @param timing_cond  condition to control the execution
        """
        self.set_state(STATE_RUNNING)

        while not self.freeze:
            self.__update_data__()
            self.set_state(STATE_RUNNING)
            with timing_cond:
                timing_cond.wait(self.refresh_time)

        self.set_state(STATE_FREEZED)

    def __update_data__(self):
        """
            Read updated data from sensor and update value to OPCUA servers.
        """
        self.set_state(STATE_READING)
        read = False
        while not read:
            try:
                temperature = self.device.temperature
                humidity = self.device.humidity
                read = True
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                read = False
        self.update_component_value(KEY_TEMPERATURE, temperature)
        self.update_component_value(KEY_HUMIDITY, humidity)

    @uamethod
    def __update_refresh_time__(self, parent, seconds):
        """
            Updates the refresh time of reading data and notify change to servers.
        """
        try:
            self.refresh_time = seconds
            #update refresh time value of all the servers
            self.update_component_value(KEY_REFRESH_TIME, seconds)
            with self.timing_cond:
                self.timing_cond.notify()
            return True
        except Exception as error:
            print(error)
            return False

class OPCUA_DHT22_Sensor(OPCUA_DHT_Sensor):
    """
        Class to manage a DHT22 sensor into an OPCUA server.
    """
    def __init__(self, pin: str, tag: str):
        super().__init__(adafruit_dht.DHT22(getattr(board, pin)), "DHT22", tag)

class OPCUA_DHT11_Sensor(OPCUA_DHT_Sensor):
    """
        Class to manage a DHT11 sensor into an OPCUA server.
    """
    def __init__(self, pin: str, tag: str):
        super().__init__(adafruit_dht.DHT11(getattr(board, pin)), "DHT11", tag)
