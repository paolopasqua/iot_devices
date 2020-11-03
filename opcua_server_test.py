from smart_sensors_utility import LoggerUtility
from opcua import ua, uamethod, Server

from pkg.opcua.sensors import OPCUA_DHT11_Sensor
from pkg.opcua.actuators import OPCUA_Relay_Actuator


def main():

    log = LoggerUtility.get_logger("dht11.log")

    log.info("**************************** START ****************************")

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://paolopasqua.site"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    d = OPCUA_DHT11_Sensor("D24","test")
    d.append_to_server(idx, objects)

    #26 19 13 6
    r1 = OPCUA_Relay_Actuator(26,"1")
    r1.append_to_server(idx, objects)
    
    r2 = OPCUA_Relay_Actuator(19,"2")
    r2.append_to_server(idx, objects)
    
    r3 = OPCUA_Relay_Actuator(13,"3")
    r3.append_to_server(idx, objects)

    r4 = OPCUA_Relay_Actuator(6,"4")
    r4.append_to_server(idx, objects)
    
    shutdown = False

    try:
    
        server.start()
        while not shutdown:
            pass

    finally:
        #close connection, remove subcsriptions, etc
        d.exit()
        server.stop()

if __name__ == "__main__":
    main()


'''
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(6,GPIO.OUT)
GPIO.output(26,GPIO.LOW)
GPIO.output(19,GPIO.LOW)
GPIO.output(13,GPIO.LOW)
GPIO.output(6,GPIO.LOW)
'''