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

def drop_all_tables_in_current_db(conn):
    """This is dangerious. All tables in the current db is deleted. Don't use it if necessary. but useful for testing case
    which is equavelent to
        SET FOREIGN_KEY_CHECKS = 0;
        DROP TABLE IF EXISTS crack_detection_result;
        DROP TABLE IF EXISTS video_processed_frame_info;
        DROP TABLE IF EXISTS video_file_id_mapping;
        DROP TABLE IF EXISTS user;
        SET FOREIGN_KEY_CHECKS = 1;"""

    command = """
        SET FOREIGN_KEY_CHECKS = 0;
        SET GROUP_CONCAT_MAX_LEN=32768;
        SET @tables = NULL;
        SELECT GROUP_CONCAT('`', table_name, '`') INTO @tables
          FROM information_schema.tables
          WHERE table_schema = (SELECT DATABASE());
        SELECT IFNULL(@tables,'dummy') INTO @tables;

        SET @tables = CONCAT('DROP TABLE IF EXISTS ', @tables);
        PREPARE stmt FROM @tables;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SET FOREIGN_KEY_CHECKS = 1;
    """
    cursor = conn.cursor(buffered=True)
    cursor.execute(command,multi=True)
    return True

def clear_all_binlog_util_now(conn):
    """delete all the binlogs. could be used after every time application is finished """
    command = """reset master;"""
    cursor = conn.cursor(buffered=True)
    cursor.execute(command)
    return True

conn = connect()

if __name__ == "__main__":
    drop_all_tables_in_current_db(conn)
    clear_all_binlog_util_now(conn)
    # conn = connect()
    # cursor = conn.cursor()
    # update_crack_detection_result_row(cursor, "F:/capstone/data/videos/darknet_output/10/00000.pkl",
    #                                 10,0)
    # update_video_processed_frame_info_plus_one_finished(cursor, 9)
    # conn.commit()
    #
    # conn.close()
    # cursor.execute("purge binary logs before '2018-07-17 20:54:00';")
