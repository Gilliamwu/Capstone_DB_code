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
    with open(video_saving_directory+"\\"+video_name + video_extension,'w') as file:
        file.write(video_file)

def generate_result_folder_for_frames(video_id):
    dst = frame_extract_directory + "\\" + str(video_id)
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
    logging.info(" >> reading {}".format(inpuy_video_f+"\\"+video_name + video_extension))
    v = video(inpuy_video_f+"\\"+video_name + video_extension)
    v.video_to_frames(result_folder)
    return v.get_frame_list(), v.video_length



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
    for i in range(len(frames_list)):
        result.append(crack_detection_result(
            video_id=video_id, frame_id=i, frame_loc=frames_list[i],detect_flag=False))
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


# for darknet
def unpack_to_dict(tup):
    label, p, rect = tup
    x, y, w, h = rect
    return {'x': x, 'y': y, 'w': w, 'h': h, 'p': p}

# pickle file
def generate_result_folder_for_pickle(video_id):
    dst = result_saving_directory + "\\" + str(video_id)
    if not os.path.exists(dst):
        os.mkdir(dst)
    return dst

def pickle_save_to_file(file_f, file_name, data, file_ext='.pkl'):
    file = file_f+"\\"+file_name+file_ext
    with open(file,'wb') as f:
        pickle.dump(data, f)
    return True

def pickle_read_file(file_f, file_name, file_ext='.pkl'):
    file = file_f + "\\" + file_name + file_ext
    with open(file,'rb') as f:
        data = pickle.load(f)
    return data