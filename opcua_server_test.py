# from smart_sensors_utility import LoggerUtility

from opcua import ua, uamethod, Server
from pkg.opcua.server.actuators import sOPCUA_Relay
from pkg.opcua.server.sensors import sOPCUA_DHT
import logging


def main():

    FORMAT = '%(asctime)-15s - %(message)s'
    logging.basicConfig(filename='opcua.log', level=logging.DEBUG, format=FORMAT)
    # logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    # log = LoggerUtility.get_logger("dht11.log")

    # log.info("**************************** START ****************************")

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://paolopasqua.site"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our nodes
    objects = server.get_objects_node()

    d = sOPCUA_DHT(sOPCUA_DHT.DHT11,"test", "D24")
    d.register_to_server(idx, objects)

    #26 19 13 6
    r1 = sOPCUA_Relay(26,"1")
    r1.register_to_server(idx, objects)
    
    r2 = sOPCUA_Relay(19,"2")
    r2.register_to_server(idx, objects)
    
    r3 = sOPCUA_Relay(13,"3")
    r3.register_to_server(idx, objects)

    r4 = sOPCUA_Relay(6,"4")
    r4.register_to_server(idx, objects)
    
    shutdown = False

    try:    
        server.start()
        while not shutdown:
            pass
    finally:
        #close connection, remove subcsriptions, etc
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