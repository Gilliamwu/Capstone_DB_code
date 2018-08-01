# # import utils
# #
# # import settings
# #
# # video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
# # frame_list, frame_length = utils.split_video_to_frames(settings.frame_extract_directory, "F:\\capstone\\data\\videos\\input",
# #                                                  "File_002", ".mov")
# # print(frame_list)
# # print(frame_length)
# from multiprocessing import Process, Queue
# import time
# import sys
#
# def reader_proc(queue):
#     ## Read from the queue; this will be spawned as a separate Process
#     while True:
#         msg = queue.get()         # Read from the queue and do nothing
#         print(" reader get ")
#         if (msg == 'DONE'):
#             break
#
# def writer(count, queue):
#     ## Write to the queue
#     for ii in range(0, count):
#         queue.put(ii)             # Write 'count' numbers into the queue
#         print("writer write")
#     queue.put('DONE')
#
# if __name__=='__main__':
#     pqueue = Queue() # writer() writes to pqueue from _this_ process
#     for count in [10**4, 10**5, 10**6,5,5,7]:
#         ### reader_proc() reads from pqueue as a separate process
#         reader_p = Process(target=reader_proc, args=((pqueue),))
#         reader_p.daemon = True
#         reader_p.start()        # Launch reader_proc() as a separate python process
#
#         _start = time.time()
#         writer(count, pqueue)    # Send a lot of stuff to reader()
#         reader_p.join()         # Wait for the reader to finish
#         print("Sending {0} numbers to Queue() took {1} seconds".format(count,
#             (time.time() - _start)))

"""Simple reader-writer locks in Python
Many readers can hold the lock XOR one and only one writer"""
import threading

version = """$Id: 04-1.html,v 1.3 2006/12/05 17:45:12 majid Exp $"""

import threading
import multiprocessing
#one thread for updating from dababase,
#one thread for image processing

from read_db_cache_test import DB_fetcher
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

from settings import MYSQL_SETTINGS, result_saving_directory
import datetime

# from models import db
from utils_non_flask import pickle_save_to_file
from yolo_running import run_yolo_in_cmd, get_data_from_console

from update_db_utils import connect, \
    update_crack_detection_result_row, \
    update_video_processed_frame_info_plus_one_finished, \
    query_detect_flag

class Image_processor(multiprocessing.Process):
    def __init__(self, share_image_queue, conn ):
        multiprocessing.Process.__init__(self)
        self.conn = conn
        self.share_image_queue = share_image_queue


    def run(self):
        while True:
            print(" wth every run into this loop? now the queue is it empty? {} size{}"
                  .format(self.share_image_queue.empty(),self.share_image_queue.qsize()))
            print(self.share_image_queue)
            while not self.share_image_queue.empty():
                i = self.share_image_queue.get()
                logging.info("<<< obtaining 1 image from queue {}".format(i["frame_loc"]))

                video_id = i['video_id']
                frame_id = i['frame_id']
                frame_loc = i["frame_loc"]
                # explicitly check if detect_flag is None or not
                detect_flag_b = query_detect_flag(self.conn, video_id, frame_id)
                print("  >>>>.given {} {}, found flag{}".format(video_id, frame_id, detect_flag_b))

                if detect_flag_b != 1:
                    frame_name = frame_loc.replace('\\',' ').replace('/',' ').split()[-1]
                    logging.info("  >> input frame path is {}, frame name {}".format(frame_loc,frame_name ))
                    # process image
                    # TODO: implement darknet
                    console_output = run_yolo_in_cmd(frame_loc)
                    output = get_data_from_console(console_output)
                    # output = [(b'crack',0.732,(218,395,347,41)),(b'crack',0.43,(18,55,67,441))]

                    # save output to a pickle and save to db
                    result_loc = result_saving_directory+"/"+str(video_id)
                    result_pic_loc = pickle_save_to_file(result_loc, frame_name.split(".")[0], output,)

                    # update crack_detection_result and change flag
                    logging.info("updating {} : {} : {}".format(video_id, frame_id, result_pic_loc ))
                    update_crack_detection_result_row(self.conn, result_pic_loc, video_id, frame_id)

                    # update video_processed_frame_info
                    # update number
                    update_video_processed_frame_info_plus_one_finished(self.conn, video_id)
                    self.conn.commit()

            time.sleep(1)
        return True

def main():
    db_conn = connect()
    # init the common queue
    logging.info("CPU count {}".format(multiprocessing.cpu_count()))
    images_details = multiprocessing.Queue()
    print("S")

    # due to the difference of DB time and our system time, we need to delete 25 hours from current date
    # so threshold time is current time + one hour

    current = datetime.datetime.now()
    # we should use our time because when passed in, it will be converted to utc time
    # current = datetime.datetime(2018,7,29, 17, 8,0) #- datetime.timedelta(minutes=30)

    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS, start_time = current)
    print("SS")
    img_server = Image_processor(images_details, db_conn)

    processes = [server_fetcher,img_server ]
    for i in processes:
        i.start()
    # images_details.join()
    # print(settings.image_processing_queue)


if __name__ == "__main__":
    main()