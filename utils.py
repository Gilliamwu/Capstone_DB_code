import os
from video import video
from models import db
from models import User, video_file_id_mapping, crack_detection_result, video_processed_frame_info
from settings import frame_extract_directory, result_saving_directory
import pickle

import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

# video save and frame extraction
def save_video_to_specific_loc(video_saving_directory, video_file, video_name, video_extension=".avi"):
    with open(video_saving_directory+"/"+video_name + video_extension,'w') as file:
        file.write(video_file)

def generate_result_folder_for_frames(video_id):
    dst = frame_extract_directory + "/" + str(video_id)
    if not os.path.exists(dst):
        os.mkdir(dst)
    return dst

def split_video_to_frames(result_folder, inpuy_video_f, video_name, video_extension=".avi"):
    """
    :param result_folder:
    :param inpuy_video_f: input video folder
    :param input_video:
    :return: frame list, total number of frames
    """
    logging.info(" >> reading {}".format(inpuy_video_f+"/"+video_name + video_extension))
    v = video(inpuy_video_f+"/"+video_name + video_extension)
    v.video_to_frames(result_folder)
    return v.get_frame_list(), v.actual_fram_lens



# ---------------DB updating from flask
def table_total_count(table):
    return db.session.query(table).count()


# -------------- INSERT TO DB
# to video_file_id_mapping
def update_video_file_id_mapping(video_name, row_n):
    print(" >>>updating now: {} with {}".format(video_name, row_n))
    # target_v = video_file_id_mapping.query.filter_by(video_location=video_name)
    # print("  >> tagret {}".format(target_v))
    # target_v.unique_id = row_n
    # db.session.commit()
    # conn = db.engine.connect()
    # stmt = video_file_id_mapping.update(). \
    #     values(unique_id=(row_n)). \
    #     where(video_file_id_mapping.video_location == video_name)
    # conn.execute(stmt)

    # db.session.query(). \
    #     filter(video_file_id_mapping.video_location == video_name). \
    #     update({"unique_id": row_n})
    # db.session.commit()
    upd = (db.session.query(video_file_id_mapping)
           .filter(video_file_id_mapping.video_location == video_name)
           )
    target = upd.one()
    target.video_id = row_n
    db.session.commit()

# to crack_detection_result
def video_plain_framelist_to_db(video_id, frames_list):
    """
    :param video_id: a int
    :param session: db.session passed from flask main
    :param frame_list:
    :return:
    """
    result = []
    print(" >>>> frame length {} \b it's length is {}".format(frames_list, len(frames_list)))
    for i in range(len(frames_list)):
        result.append(crack_detection_result(
            video_id=video_id, frame_id=i+1, frame_loc=frames_list[i],detect_flag=False))
    db.session.bulk_save_objects(result)
    db.session.commit()
    logging.info("  finished save frame list to db.check?")

# to crack_detection_result
def video_processed_frame_info_to_db(video_id, frame_id, result_loc):
    catch_row = (db.session.query(crack_detection_result).filter(
        crack_detection_result.video_id == video_id and crack_detection_result.frame_id ==frame_id)).first()
    if catch_row is None:
        logging.error("THE TARGET video_id{}, frame{} couldn't be found".format(video_id, frame_id))
    catch_row.result_loc = result_loc
    catch_row.detect_flag = True
    db.session.commit()

# to video_processed_frame_list
def insert_pain_video_processed_frame_info( video_id, total_n):
    db.session.add(video_processed_frame_info(video_id,total_n))
    db.session.commit()

# to video_processed_frame_list, change every column
def update_video_processed_frame_info_total_frames( video_id, total_n, finished_n):
    catch_row = (db.session.query(video_processed_frame_info).filter(
        video_processed_frame_info.video_id == video_id)).first()
    catch_row.total_frames = total_n
    catch_row.processed_frames_n = finished_n
    db.session.commit()

# to video_processed_frame_list, plus 1 to processed_n
def update_video_processed_frame_info_processed_frames_plus_one(video_id):
    catch_row = (db.session.query(video_processed_frame_info).filter(
        video_processed_frame_info.video_id == video_id)).first()
    catch_row.total_frames = catch_row.processed_frames_n + 1
    db.session.commit()

# to video_processed_frame_list, change processed_n
def update_video_processed_frame_info_processed_frames( video_id, processed_n):
    catch_row = (db.session.query(video_processed_frame_info).filter(
        video_processed_frame_info.video_id == video_id)).first()
    catch_row.total_frames = processed_n
    db.session.commit()

def db_check_if_vid_exist(vid_name):
    vid_name = vid_name.strip()
    if vid_name.isdigit():
        total_v_len = table_total_count(video_file_id_mapping)
        if int(vid_name) > 0 and int(vid_name) <= total_v_len:
            return True, int(vid_name)
        return False, "vid should be in range 0 to {}".format(total_v_len)
    print(" >>>>>>>>>>>>>the vid received is {}".format(vid_name))
    return False, "currently vid should consists only of numbers"

def db_check_if_frame_id_exist(vid_name, frame_index):
    # known the vid is valid.
    if isinstance(frame_index, int):
        current_total = db.session.query(video_processed_frame_info).filter(video_processed_frame_info.video_id == vid_name).first().total_frames

        #current_total = crack_detection_result.query.filter_by(video_id = vid_name).count()
        if frame_index <= current_total and frame_index > 0:
            return True, frame_index
    return False, current_total