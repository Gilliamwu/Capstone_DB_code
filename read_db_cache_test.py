from pymysqlreplication import BinLogStreamReader
import time
import multiprocessing
import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
import datetime
from settings import MYSQL_SETTINGS

from pymysqlreplication.tests import base

from pymysqlreplication.row_event import (
    # DeleteRowsEvent,
    # UpdateRowsEvent,
    WriteRowsEvent,
)

def convert_to_second_int(datetimein):
    return time.mktime(datetimein.timetuple()) #(datetimein-datetime.datetime(1970,1,1)).total_seconds()

class DB_fetcher(multiprocessing.Process):
    def __init__(self, share_image_queue, MYSQL_SETTINGS ,target_schema = "capstone",
                 target_table = "crack_detection_result", last_read_id = 0,
                 start_time = datetime.datetime(1970,1,2,0,1,0)): # 1970,1,1 is almost 0 second
        multiprocessing.Process.__init__(self)
        self.share_image_queue = share_image_queue
        self.target_schema = target_schema
        self.target_table = target_table
        self.last_read_id = last_read_id
        self.skip_to_timestamp = convert_to_second_int(start_time)

    def run(self):
        while True:
            self.stream = BinLogStreamReader(
                connection_settings=MYSQL_SETTINGS,
                only_events=[WriteRowsEvent],  # [DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
                server_id=3,
                slave_heartbeat=1
                ,skip_to_timestamp = self.skip_to_timestamp)

            # self.idx = 0
            # self.show_slave_status()
            for binlogevent in self.stream:
                prefix = "%s:%s:" % (binlogevent.schema, binlogevent.table)
                if prefix == self.target_schema + ":" + self.target_table + ":":
                    # print(binlogevent.rows)
                    for new_update_row in binlogevent.rows:
                        logging.info(" >>> find new row {}".format(new_update_row))
                        # format for a row: {'values':
                        #       {'video_id': 1, 'frame_id': 4, 'insert_time': datetime.datetime(2008, 6, 19, 0, 0),
                        #       'frame_loc': 'RANDOM_LL', 'detect_flag': boolean, 'result_loc': None}}
                        if new_update_row["values"]["detect_flag"] == 0 and  new_update_row["values"]['insert_time'] is not None:
                            # TODO: maybe edit here
                            #logging.info(" >>> for this row, the flag is {}".format(new_update_row['detect_flag']))
                            self.share_image_queue.put(new_update_row["values"])
                            logging.info(" >>> adding 1 image to queue {}".format(new_update_row))
            self.skip_to_timestamp = convert_to_second_int(datetime.datetime.now())
            time.sleep(6)

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


#
# class DB_fetcher( base.PyMySQLReplicationTestCase ):
#     def __init__(self, share_image_queue, MYSQL_SETTINGS ,target_schema = "capstone",
#                  target_table = "new_table", last_read_id = 0,
#                  skip_to_timestamp = datetime.datetime(1900,1,1,0,0,0)):
#         # multiprocessing.Process.__init__(self)
#         self.share_image_queue = share_image_queue
#         self.target_schema = target_schema
#         self.target_table = target_table
#         self.last_read_id = last_read_id
#         # self.idx = 0
#
#         timestamp = self.execute('SELECT UNIX_TIMESTAMP()').fetchone()[0]
#         self.skip_to_timestamp = skip_to_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    #
    # def run(self):
    #     while True:
    #         self.stream = BinLogStreamReader(
    #             connection_settings=MYSQL_SETTINGS,
    #             only_events=[WriteRowsEvent],  # [DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent],
    #             server_id=3,
    #             slave_heartbeat=1
    #             ,
    #             skip_to_timestamp = self.skip_to_timestamp)
    #
    #         # self.idx = 0
    #         # self.show_slave_status()
    #         for binlogevent in self.stream:
    #             prefix = "%s:%s:" % (binlogevent.schema, binlogevent.table)
    #             if prefix == self.target_schema + ":" + self.target_table + ":":
    #                 # print(binlogevent.rows)
    #                 for new_update_row in binlogevent.rows:
    #                     logging.info(" >>> find new row {}".format(new_update_row))
    #                     # format for a row: {'values':
    #                     #       {'map_id': 1, 'timestamp': datetime.datetime(2008, 6, 19, 0, 0),
    #                     #       'image_location': 'RANDOM_LL', 'crack_detect': None, 'result_locatoin': None}}
    #                     if new_update_row["values"]["crack_detect"] is None:
    #                         self.share_image_queue.put(new_update_row["values"])
    #                         logging.info(" >>> adding 1 image to queue")
    #         self.skip_to_timestamp = datetime.datetime.now().time()
    #         time.sleep(3)
    #
    # def close_stream(self):
    #     self.stream.close()

if __name__ == "__main__":
    images_details = multiprocessing.Queue()
    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS)
    server_fetcher.start()


