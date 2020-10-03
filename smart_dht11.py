import time
import board
import adafruit_dht
import logger
import database

log = logger.get_logger("dht11.log")

log.info("**************************** START ****************************")

to_connect = True
while to_connect:
    try:
        time.sleep(15)

        log.info("Connecting to db...")
        connection = database.get_connection()
        log.info("Connected.")
        to_connect = False

    except Exception as e:
        log.error("Exception on connecting: %s" % e)
        to_connect = True


# Initial the dht device, with data pin connected to:
log.info("Initializing the device DHT11 on pin 18...")
dhtDevice = adafruit_dht.DHT11(board.D18)

time_delta = 30
tag = "test"
sql = "INSERT INTO `dht11` (`tag`, `temperature`, `humidity`) VALUES (%s, %s, %s)"
    
# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

log.info("Start collecting data...")
while True:
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity

        try:
            log.debug("Data: temp: %.2f °C  ;  humidity: %.2f " % (temperature_c, humidity))
            with connection.cursor() as cursor:
                # Create a new record
                log.debug("Executing query: %s" % (sql % (tag,temperature_c,humidity)))
                cursor.execute(sql, (tag,temperature_c,humidity))
            # connection is not autocommit by default. So you must commit to save your changes.
            connection.commit()
        except Exception as e:
            log.error("Exception: %s\nOn executin query: %s" % (e,(sql % (tag,temperature_c,humidity))) )

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        log.error(error.args[0])
        continue
    except Exception as error:
        dhtDevice.exit()
        connection.close()
        log.error("Exiting after exception: %s" % error)
        raise error
    
    #read pause
    time.sleep(time_delta)