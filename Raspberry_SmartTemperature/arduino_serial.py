import logging
import serial
import json
from datetime import datetime
import os
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(os.path.dirname(__file__) + "/arduino_serial.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info("**************************** START ****************************")

def check_file_or_create(path):
    try:
        f = open(path, 'r')
        f.close()
    except:
        f = open(path,'w')
        f.close()

logger.info("Checking files")
check_file_or_create(os.path.dirname(__file__) + "/data/temperature.csv")
check_file_or_create(os.path.dirname(__file__) + "/data/humidity.csv")
check_file_or_create(os.path.dirname(__file__) + "/data/heat_index.csv")

while 1:
    logger.info("Opening serial on port '/dev/ttyUSB0'; baud rate: 9600")
    try:
        arduinoSerialData = serial.Serial('/dev/ttyUSB0',9600)
    except:
        logger.error("No device found.")
        time.sleep(10)
    else:
        try:
            while 1:
                if(arduinoSerialData.inWaiting()>0):
                    myData = arduinoSerialData.readline()
                    logger.info("Receiving data from serial... %s" % myData)

                    try:
                        myData = myData.decode('utf-8')
                        logger.info("Parsing data into json... %s" % myData)
                        data = json.loads(myData)
                    except Exception as e:
                        logger.error("Exception on parsing: %s" % e)
                    else:
                        date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
                        
                        logger.info("Opening csv files...")
                        temp = open(os.path.dirname(__file__) + "/data/temperature.csv", 'a')
                        hum = open(os.path.dirname(__file__) + "/data/humidity.csv", 'a')
                        hic = open(os.path.dirname(__file__) + "/data/heat_index.csv", 'a')
                        logger.info("Writing files...")
                        temp.write("%s;%.2f;%.2f;%.2f;%.2f\n" % (date,data['temperature']['actual'],data['temperature']['average'],data['temperature']['minimum'],data['temperature']['maximum']))
                        hum.write("%s;%.2f;%.2f;%.2f;%.2f\n" % (date,data['humidity']['actual'],data['humidity']['average'],data['humidity']['minimum'],data['humidity']['maximum']))
                        hic.write("%s;%.2f;%.2f;%.2f;%.2f\n" % (date,data['hic']['actual'],data['hic']['average'],data['hic']['minimum'],data['hic']['maximum']))
                        logger.info("Closing files...")
                        temp.close()
                        hum.close()
                        hic.close()
        except Exception as e:
            logger.error("Exception: %s" % e)
    