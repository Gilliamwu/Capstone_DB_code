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
from utils import pickle_save_to_file, \
    update_video_processed_frame_info_processed_frames_plus_one, \
    video_processed_frame_info_to_db

class Image_processor(multiprocessing.Process):
    def __init__(self,share_image_queue ):
        multiprocessing.Process.__init__(self)
        self.share_image_queue = share_image_queue

    def run(self):
        while True:
            print(self.share_image_queue)
            while not self.share_image_queue.empty():
                i = self.share_image_queue.get()
                logging.info("<<< obtaining 1 image from queue {}".format(i["frame_loc"]))

                video_id = i['video_id']
                frame_id = i['frame_id']
                frame_loc = i["frame_loc"]

                print(frame_loc)
                frame_name = frame_loc.replace('\\',' ').replace('/',' ').split()[-1]
                logging.info("  >> input frame path is {}, frame name {}".format(frame_loc,frame_name ))
                # process image
                # TODO: implement darknet

                output = [(b'crack',0.732,(218,395,347,41)),(b'crack',0.43,(18,55,67,441))]
                # save output to a pickle and save to db
                result_loc = result_saving_directory+"\\"+str(video_id)
                pickle_save_to_file(result_loc, frame_name, output,)

                # update crack_detection_result and change flag
                logging.info("updating {} : {} : {}".format(video_id, frame_id, result_loc ))
                video_processed_frame_info_to_db(video_id, frame_id, result_loc )

                # update video_processed_frame_info
                # update number
                update_video_processed_frame_info_processed_frames_plus_one(video_id)
            time.sleep(1)
        return True

def main():
    # init the common queue
    logging.info("CPU count {}".format(multiprocessing.cpu_count()))
    images_details = multiprocessing.Queue()
    print("S")

    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS,start_time = datetime.datetime(2018,7,27,13,0,0))
    print("SS")
    img_server = Image_processor(images_details)

    processes = [server_fetcher,img_server ]
    for i in processes:
        i.start()
    # images_details.join()
    # print(settings.image_processing_queue)

if __name__ == "__main__":
    main()