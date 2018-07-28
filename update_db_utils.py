import mysql.connector
from mysql.connector import errorcode
import datetime
from settings import MYSQL_SETTINGS
from settings import MYSQL_connection_setting



def connect():
    try:
        cnx = mysql.connector.connect(user=MYSQL_SETTINGS['user'],
                                      password=MYSQL_SETTINGS['passwd'],
                                      host=MYSQL_SETTINGS["host"],
                                      port=MYSQL_connection_setting['port'],
                                      database = MYSQL_connection_setting["database"])
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None
    return cnx

def update_crack_detection_result_row(conn, result_loc, video_id, frame_id):
    command = """UPDATE crack_detection_result
                SET result_loc=%s, detect_flag=1
                where video_id=%s AND frame_id=%s
            """
    cursor = conn.cursor(buffered=True)
    cursor.execute(command, (result_loc, video_id, frame_id,))
    conn.commit()

def update_video_processed_frame_info_plus_one_finished(conn,video_id):
    command = """
            UPDATE video_processed_frame_info
            set processed_frames_n = processed_frames_n + 1
            where video_id = %s
            """
    cursor = conn.cursor(buffered=True)
    cursor.execute(command, (video_id,))
    conn.commit()

def query_detect_flag(conn, video_id, frame_id):
    command = """
        SELECT detect_flag FROM crack_detection_result
        where video_id = %s and frame_id = %s
    """
    cursor = conn.cursor(buffered=True)
    result = None
    # try: result is like (1,)
    cursor.execute(command, (video_id, frame_id))
    result = cursor.fetchone()
    # except Exception as e:
    #     print("!!!!!SELECT detect_flag FROM crack_detection_result where video_id = {} and frame_id = {}".format( video_id, frame_id) )
    #     print(e)
    return result[0]

conn = connect()
cursor = conn.cursor()

if __name__ == "__main__":
    conn = connect()
    cursor = conn.cursor()
    update_crack_detection_result_row(cursor, "F:\\capstone\\data\\videos\\darknet_output\\10\\00000.pkl",
                                    10,0)
    update_video_processed_frame_info_plus_one_finished(cursor, 9)
    conn.commit()

    conn.close()
    # cursor.execute("purge binary logs before '2018-07-17 20:54:00';")
