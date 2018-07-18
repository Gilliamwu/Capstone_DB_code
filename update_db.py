import mysql.connector
from mysql.connector import errorcode
import datetime


def connect(database='capstone'):
    MYSQL_SETTINGS = {
        "host": 'localhost',
        "port": 3306,
        "user": "root",
        "passwd": "123456"
    }

    try:
        cnx = mysql.connector.connect(user=MYSQL_SETTINGS['user'],
                                      password=MYSQL_SETTINGS['passwd'],
                                      host=MYSQL_SETTINGS["host"],
                                      port=3306,
                                      database = database)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    return cnx

def update_row(cursor, crack_detect, result_locatoin, map_id, timestamp,image_location,target_table = 'new_table' ):
    command = """UPDATE {}
                SET crack_detect=%s,
                result_locatoin=%s
                where map_id=%s AND timestamp=%s AND image_location=%s
            """.format(target_table)
    cursor.execute(command, (crack_detect, result_locatoin, map_id, timestamp,image_location))

if __name__ == "__main__":
    schema = 'capstone'
    conn = connect()
    cursor = conn.cursor()
    update_row(cursor, 255, "result_test", 1, datetime.datetime(2008, 6, 19, 0, 0), 'RANDOM_L')
    conn.commit()
    conn.close()
    # cursor.execute("purge binary logs before '2018-07-17 20:54:00';")
