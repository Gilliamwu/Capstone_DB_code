from flask import request, jsonify, Flask
from flask_api import status
from functools import wraps
from models import db
from settings import video_saving_directory

import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

from utils import split_video_to_frames, \
    table_total_count, \
    update_video_file_id_mapping, \
    video_plain_framelist_to_db, \
    generate_result_folder_for_frames,\
    insert_pain_video_processed_frame_info,\
    update_video_processed_frame_info_total_frames,\
    db_check_if_vid_exist, \
    db_check_if_frame_id_exist

from utils_non_flask import generate_result_folder_for_pickle, \
    pickle_read_file_direct, \
    unpack_to_dict

application = app = Flask(__name__)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask:p2s5w0rD@flasktest.cfparnusqsew.us-west-2.rds.amazonaws.com/aeolusdb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/capstone'
db.app = application
db.init_app(application)
import os
from models import User,video_file_id_mapping, crack_detection_result, video_processed_frame_info


# TODO: later rmv--- not really used, for testing only
from flask import render_template
from flask import request
admin = User('admin1', 'admin1@example.com')
db.create_all()
print("user table created")
# db.session.add(admin)
db.session.commit()
User.query.all()
User.query.filter_by(username='admin').first()

###################################################################
###################################################################

users = {
    "a":"b",
    "Admin1": "admin_password",
    "User1": "password1"
    }

def is_valid_user(username, password):
    return username in users and users[username] == password

def ask_for_login(has_auth):
    '''
    Checks for login
    '''
    if not has_auth:
        message = {'message': "Login Required"}
    else:
        message = {'message': "Invalid Credentials"}

    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="AEOLUS Login"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return ask_for_login(False)
        elif not is_valid_user(auth.username, auth.password):
            return ask_for_login(True)
        return f(*args, **kwargs)
    return decorated

@application.route("/", methods=['POST'])
@requires_auth
def main_auth():
    return "Hello World!", status.HTTP_200_OK

@application.route("/video", methods=['POST'])
@requires_auth
def video_upload():
    if 'video' in request.files:
        submitted_file = request.files['video']

        # get the id this video should have and save to settings.video_saving_directory folder
        video_id = table_total_count(video_file_id_mapping)+1
        output_video_name = "test{}".format(video_id)
        output_video_ext = ".avi"
        video_loc = video_saving_directory +"/"+output_video_name+output_video_ext
        submitted_file.save(video_loc)

        # add the mapping to db
        video = video_file_id_mapping(video_location=video_loc)
        db.session.add(video)
        print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
        update_video_file_id_mapping(video_loc, video_id)
        db.session.commit()
        logging.info("  >>> given video saved to db: {}".format(video))

        # extract frame
        frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
        # just to create a pickle folder
        generate_result_folder_for_pickle(video_id)

        frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
                                            video_saving_directory, output_video_name, output_video_ext)
        print("  >>> frames extracted. with video id {}".format(video_id))

        # save frames to db
        video_plain_framelist_to_db(video_id, frame_list)
        # print("video id {}and frame list is {}".format(video_id, frame_list))
        print("  >>> save frames to db already")

        # save frames number to db
        insert_pain_video_processed_frame_info(video_id, frame_length)
        print("  >>> save total number to db")

        # data = {'uid': uid, 'frames': n_frames}
        data = {'uid': video_id, 'frames': frame_length}
        resp = jsonify(data)
        resp.status_code = 201
        return resp
    else:
        return "", status.HTTP_400_BAD_REQUEST

@application.route("/video/<string:vid_name>/frames", methods=['GET'])
@requires_auth
def video_frame_status_get(vid_name):
    # check if video in db
    vid_exist_flag, reason_or_processed_name = db_check_if_vid_exist(vid_name)
    if vid_exist_flag:
        target_v_info = video_processed_frame_info.query.filter_by(video_id = reason_or_processed_name).first()
        n_frames = target_v_info.total_frames
        # n_frames =
        completed_frames = target_v_info.processed_frames_n
        # n_frames = 200
        # completed_frames = 6 #[1, 2, 3]
        data = {'frames': n_frames, 'completed_frames': completed_frames}
        print(" >>> INFO: frame data: {}".format(data))
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    return reason_or_processed_name, status.HTTP_400_BAD_REQUEST

@application.route("/video/<string:vid_name>/frames/<int:frame_index>", methods=['GET'])
@requires_auth
def video_frame_get(vid_name, frame_index):
    vid_exist_flag, reason_or_processed_name = db_check_if_vid_exist(vid_name)
    if vid_exist_flag:
    # check if video in db
        frame_existence_flag, id_or_msg = db_check_if_frame_id_exist(vid_name, frame_index)

        print(" >>> ERROR: video, {} frame {} get {} {}".format(reason_or_processed_name, frame_index, frame_existence_flag, id_or_msg))
        if frame_existence_flag:
            # check if frame processed
            try:
                target_frame_row = crack_detection_result.query.filter_by(video_id=reason_or_processed_name, frame_id = frame_index).first()
            except:
                print( " >>>>>> ERROR video, {} frame {} get {} {}, {}".format(reason_or_processed_name, frame_index, frame_existence_flag, id_or_msg, crack_detection_result.query.filter_by(video_id=reason_or_processed_name, frame_id = frame_index)))

            if target_frame_row.detect_flag == 1:

                print(">>>read {} {} {}".format(reason_or_processed_name, frame_index, target_frame_row))
                lst_of_tup = pickle_read_file_direct(target_frame_row.result_loc)
                print(">>>read {}".format(target_frame_row.result_loc))

                boxes = [unpack_to_dict(t) for t in lst_of_tup]
                print(" FLAG: frame processed finished")
                print(boxes)

                data = {'boxes': boxes}
                resp = jsonify(data)
                resp.status_code = 200
                print(" >>> info: get data: {}".format(data))
                return resp
            # frame not yet processed
            else:
                print(" Frame not processed yet")
                return "Frame not processed yet", status.HTTP_204_NO_CONTENT
        else:
            return "this frame doesn't exist. framd id should in range 1 to {}".format(id_or_msg)
    else:
        return reason_or_processed_name, status.HTTP_400_BAD_REQUEST

@application.route("/test", methods=['GET'])
@requires_auth
def test_video_get():
    print("============HELLO WORLD this is the test page")
    # video_id = 1
    # frame_list = ["F:\\capstone\\data\\videos\\extacted_frames/0000.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00001.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00002.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00003.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00004.jpg"]
    # frame_frame_length = 5
    # video_plain_framelist_to_db(video_id, frame_list)
    return render_template("home.html"), status.HTTP_200_OK

@application.route("/test", methods=['POST'])
@requires_auth
def test_video():
    # video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
    print("============receive post from test page")
    if request.form:
        video_loc = request.form.get("video_loc")

        video_id = table_total_count(video_file_id_mapping)+1
        output_video_name = "PICT0378"
        output_video_ext = ".avi"
        this_video_saving_directory = "F:/capstone/data/videos/dumped_video"
        video_loc = video_saving_directory +"/"+output_video_name+output_video_ext
        # video_loc = "F:\\capstone\\data\\videos\\inputFile_002.mov\\Laser Road Imaging System.avi"

        video = video_file_id_mapping(video_location=video_loc)
        db.session.add(video)
        print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
        update_video_file_id_mapping(video_loc, video_id)
        db.session.commit()
        logging.info("  >>> given video saved to db: {}".format(video))

        #extract frames
        frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
        # create pickle folder for result
        generate_result_folder_for_pickle(video_id)


        frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
                                                         this_video_saving_directory,output_video_name,output_video_ext)
        print("  >>> frames extracted.")
        # save frames to db
        video_plain_framelist_to_db(video_id, frame_list)
        print("video id {}and frame listi is {}".format(video_id, frame_list))
        print("  >>> save frames to db already")
        # save number to db
        insert_pain_video_processed_frame_info(video_id, frame_length)
        print("  >>> save total number to db")
    print("  > finished upload")

    return render_template("home.html"), status.HTTP_200_OK
    # return "Hello World!"

if __name__ == "__main__":
    app.run(host= '0.0.0.0', debug=True)
    # application.run(debug=True)