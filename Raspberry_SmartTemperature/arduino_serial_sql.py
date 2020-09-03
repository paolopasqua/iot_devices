import logging
import serial
import json
from datetime import datetime
import os
import time
import pymysql

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler(os.path.dirname(__file__) + "/arduino_serial.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info("**************************** START ****************************")

while 1:
    try:
        time.sleep(15)

        logger.info("Connecting to db...")
        # Connect to the database
        connection = pymysql.connect(host='localhost',
                                    user='user',
                                    password='user',
                                    db='smart_temp',
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        logger.info("Connected user@localhost to db smart_temp")

        logger.info("Opening serial on port '/dev/ttyUSB0'; baud rate: 9600")
        try:
            arduinoSerialData = serial.Serial('/dev/ttyUSB0',9600)
        except:
            logger.error("No device found.")
        else:
            try:
                prev_id = 0

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
                            if data['id'] != prev_id:
                                prev_id = data['id'] #so if the line is read 2 times it will no be elaborated

                                date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")
                                
                                logger.info("Executing insert into tables...")
                                try:
                                    with connection.cursor() as cursor:
                                        # Create a new record
                                        sql = "INSERT INTO `temperature` (`date`, `actual`, `average`, `minimum`, `maximum`) VALUES (%s, %s, %s, %s, %s)"
                                        logger.debug("Executing query: %s" % (sql % (date,data['temperature']['actual'],data['temperature']['average'],data['temperature']['minimum'],data['temperature']['maximum'])))
                                        cursor.execute(sql, (date,data['temperature']['actual'],data['temperature']['average'],data['temperature']['minimum'],data['temperature']['maximum']))
                                        sql = "INSERT INTO `humidity` (`date`, `actual`, `average`, `minimum`, `maximum`) VALUES (%s, %s, %s, %s, %s)"
                                        logger.debug("Executing query: %s" % (sql % (date,data['humidity']['actual'],data['humidity']['average'],data['humidity']['minimum'],data['humidity']['maximum'])))
                                        cursor.execute(sql, (date,data['humidity']['actual'],data['humidity']['average'],data['humidity']['minimum'],data['humidity']['maximum']))
                                        sql = "INSERT INTO `hic` (`date`, `actual`, `average`, `minimum`, `maximum`) VALUES (%s, %s, %s, %s, %s)"
                                        logger.debug("Executing query: %s" % (sql % (date,data['hic']['actual'],data['hic']['average'],data['hic']['minimum'],data['hic']['maximum'])))
                                        cursor.execute(sql, (date,data['hic']['actual'],data['hic']['average'],data['hic']['minimum'],data['hic']['maximum']))

                                    # connection is not autocommit by default. So you must commit to save
                                    # your changes.
                                    logger.info("Committing data.")
                                    connection.commit()
                                except Exception as e:
                                    logger.error("Exception on inserting: %s" % e)

            except Exception as e:
                logger.error("Exception on running: %s" % e)
        
        logger.info("Closing connection to db")
        connection.close()

    except Exception as e:
        logger.error("Exception on connecting: %s" % e)
        
    