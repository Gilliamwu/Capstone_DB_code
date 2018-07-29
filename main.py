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
                    result_loc = result_saving_directory+"\\"+str(video_id)
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

    current_date = datetime.datetime.now()
    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS,start_time = current_date)
    print("SS")
    img_server = Image_processor(images_details, db_conn)

    processes = [server_fetcher,img_server ]
    for i in processes:
        i.start()
    # images_details.join()
    # print(settings.image_processing_queue)


if __name__ == "__main__":
    main()