
import pymysql
import json


class DatabaseUtility(object):
    """
    docstring
    """
    JSON_KEY_HOST = 'host'
    JSON_KEY_USERNAME = 'username'
    JSON_KEY_PASSWORD = 'password'
    JSON_KEY_DATABASE = 'database'

    def get_connection(json_path):
        with open(json_path) as f:
            data = json.load(f)
        
        # Connect to the database
        connection = pymysql.connect(host=data[DatabaseUtility.JSON_KEY_HOST],
                                    user=data[DatabaseUtility.JSON_KEY_USERNAME],
                                    password=data[DatabaseUtility.JSON_KEY_PASSWORD],
                                    db=data[DatabaseUtility.JSON_KEY_DATABASE],
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        return connection