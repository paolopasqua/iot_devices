
import pymysql

def get_connection():
    # Connect to the database
    connection = pymysql.connect(host='localhost',
                                user='user',
                                password='user',
                                db='smart_sensors',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection