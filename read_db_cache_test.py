from pymysqlreplication import BinLogStreamReader
import time
import multiprocessing
import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
import datetime

import mysql.connector
from mysql.connector import errorcode


from pymysqlreplication.row_event import (
    # DeleteRowsEvent,
    # UpdateRowsEvent,
    WriteRowsEvent,
)

MYSQL_SETTINGS = {
    "host": 'localhost',
    "port": 3306,
    "user": "root",
    "passwd": "123456"
}

class DB_fetcher(multiprocessing.Process):
    def __init__(self, share_image_queue, MYSQL_SETTINGS ,target_schema = "capstone",
                 target_table = "new_table", last_read_id = 0,
                 skip_to_timestamp = datetime.datetime(1900,1,1,0,0,0)):
        multiprocessing.Process.__init__(self)
        self.share_image_queue = share_image_queue
        self.target_schema = target_schema
        self.target_table = target_table
        self.last_read_id = last_read_id
        self.idx = 0

    def run(self):
        while True:
            self.stream = BinLogStreamReader(
                connection_settings=MYSQL_SETTINGS,
                only_events=[WriteRowsEvent],  # [DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
                server_id=3,
                slave_heartbeat=1)

            self.idx = 0
            self.show_slave_status()
            for binlogevent in self.stream:
                # print(">>> binlogevent {}".format(binlogevent))
                if (self.idx < self.last_read_id):
                    pass
                else:
                    prefix = "%s:%s:" % (binlogevent.schema, binlogevent.table)
                    if prefix == self.target_schema + ":" + self.target_table + ":":
                        # print(binlogevent.rows)
                        for new_update_row in binlogevent.rows:
                            logging.info(" >>> find new row {}".format(new_update_row))
                            # format for a row: {'values':
                            #       {'map_id': 1, 'timestamp': datetime.datetime(2008, 6, 19, 0, 0),
                            #       'image_location': 'RANDOM_LL', 'crack_detect': None, 'result_locatoin': None}}
                            if new_update_row["values"]["crack_detect"] is None:
                                self.share_image_queue.put(new_update_row["values"])
                                logging.info(" >>> adding 1 image to queue")
                    self.last_read_id += 1
                self.idx += 1
            time.sleep(3)

    def close_stream(self):
        self.stream.close()


# def main(target_schema = "capstone", target_table = "new_table", last_read_id = 0):
#     """
#     details of binLogStreamRead: https://github.com/noplay/python-mysql-replication/blob/master/pymysqlreplication/binlogstream.py
#     :return:
#     """
#     stream = BinLogStreamReader(
#             connection_settings=MYSQL_SETTINGS,
#             only_events= [WriteRowsEvent], #[DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
#             server_id = 3,
#             slave_heartbeat = 1)
#
#     print(stream)
#     print(">>>>>>>>>> getting update")
#     for binlogevent in stream:
#         # print(">>> binlogevent {}".format(binlogevent))
#
#         prefix = "%s:%s:" % (binlogevent.schema, binlogevent.table)
#         # print(prefix)
#         if prefix == target_schema+":"+target_table+":":
#             new_update_rows = binlogevent.rows[last_read_id:]
#             for vals in new_update_rows:
#                 # format: {'values':
#                 #       {'map_id': 1, 'timestamp': datetime.datetime(2008, 6, 19, 0, 0),
#                 #       'image_location': 'RANDOM_LL', 'crack_detect': None, 'result_locatoin': None}}
#                 if vals["values"]["crack_detect"] is None:
#                     # settings.image_processing_queue.put(vals["values"])
#                     print(" >>> adding 1 image to queue")
#                 last_read_id += 1
#         time.sleep(1)
#     stream.close()

if __name__ == "__main__":
    images_details = multiprocessing.Queue()
    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS)
    server_fetcher.start()


