import threading
import multiprocessing
#one thread for updating from dababase,
#one thread for image processing

from read_db_cache_test import DB_fetcher
import time
import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

MYSQL_SETTINGS = {
    "host": 'localhost',
    "port": 3306,
    "user": "root",
    "passwd": "123456"
}

class Image_processor(multiprocessing.Process):
    def __init__(self,share_image_queue ):
        multiprocessing.Process.__init__(self)
        self.share_image_queue = share_image_queue

    def run(self):
        while True:
            while not self.share_image_queue.empty():
                i = self.share_image_queue.get()

                logging.info("<<< obtaining 1 image from queue {}".format(i["image_location"]))
            time.sleep(1)
        return



def main():
    # init the common queue
    logging.info("CPU count {}".format(multiprocessing.cpu_count()))
    images_details = multiprocessing.Queue()
    print("S")

    server_fetcher = DB_fetcher(images_details, MYSQL_SETTINGS)
    print("SS")
    img_server = Image_processor(images_details)

    processes = [server_fetcher,img_server ]
    for i in processes:
        i.start()

    # images_details.join()
    # print(settings.image_processing_queue)


if __name__ == "__main__":
    main()