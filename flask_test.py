from flask import request, jsonify, Flask
from flask_api import status
from functools import wraps
from models import db

import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

from utils import split_video_to_frames, \
    table_total_count, \
    update_video_file_id_mapping, \
    video_plain_framelist_to_db, \
    generate_result_folder_for_frames,\
    insert_pain_video_processed_frame_info,\
    update_video_processed_frame_info_total_frames,\
    generate_result_folder_for_pickle, \
    unpack_to_dict

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/capstone'

db.app = app
db.init_app(app)
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

@app.route("/", methods=['POST'])
@requires_auth
def main_auth():
    return "Hello World!", status.HTTP_200_OK

@app.route("/video", methods=['POST'])
@requires_auth
def video_upload():
    if 'video' in request.files:
        submitted_file = request.files['video']
        # your save code goes here
        submitted_file.save("test1.avi")
        video_loc = 'test1'
        # end of save code
        # uid = 'asdf12345'
        # n_frames = 200

        video = video_file_id_mapping(video_location=video_loc)
        db.session.add(video)
        video_id = table_total_count(video_file_id_mapping)
        print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
        update_video_file_id_mapping(video_loc, video_id)
        db.session.commit()
        logging.info("  >>> given video saved to db: {}".format(video))
        frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
        frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
                                            os.getcwd(), video_loc, ".avi")
        print("  >>> frames extracted.")
        # save frames to db
        video_plain_framelist_to_db(video_id, frame_list)
        print("video id {}and frame listi is {}".format(video_id, frame_list))
        print("  >>> save frames to db already")
        # save number to db
        insert_pain_video_processed_frame_info(video_id, frame_length)
        print("  >>> save total number to db")

        # data = {'uid': uid, 'frames': n_frames}
        data = {'uid': video_id, 'frames': frame_length}
        resp = jsonify(data)
        resp.status_code = 201
        return resp
    else:
        return "", status.HTTP_400_BAD_REQUEST

@app.route("/video/<string:vid_name>/frames", methods=['GET'])
@requires_auth
def video_frame_status_get(vid_name):
    # check if video in db
    if True:
        n_frames = 200
        completed_frames = 6 #[1, 2, 3]
        data = {'frames': n_frames, 'completed_frames': completed_frames}
        resp = jsonify(data)
        resp.status_code = 200
        return resp
    else:
        return "", status.HTTP_400_BAD_REQUEST

@app.route("/video/<string:vid_name>/frames/<int:frame_index>", methods=['GET'])
@requires_auth
def video_frame_get(vid_name, frame_index):
    # check if video in db
    if True:
        # check if frame processed
        if True:
            lst_of_tup = []

            boxes = [unpack_to_dict(t) for t in lst_of_tup]

            box1 = {'x': 0, 'y': 0, 'w': 1, 'h': 1, 'p': 0.49}
            box2 = {'x': 0, 'y': 0, 'w': 1, 'h': 1, 'p': 0.49}
            boxes = [box1, box2]
            data = {'boxes': boxes}
            resp = jsonify(data)
            resp.status_code = 200
            return resp
        # frame not yet processed
        else:
            return "", status.HTTP_204_NO_CONTENT
    else:
        return "", status.HTTP_400_BAD_REQUEST

@app.route("/test", methods=['GET'])
@requires_auth
def test_video_get():
    print("============HELLO WORLD the test page")
    # video_id = 1
    # frame_list = ["F:\\capstone\\data\\videos\\extacted_frames/0000.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00001.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00002.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00003.jpg",
    #               "F:\\capstone\\data\\videos\\extacted_frames/00004.jpg"]
    # frame_frame_length = 5
    # video_plain_framelist_to_db(video_id, frame_list)
    return render_template("home.html"), status.HTTP_200_OK

@app.route("/test", methods=['POST'])
@requires_auth
def test_video():
    # video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
    print("============receive post frmo test page")
    if request.form:
        video_loc = request.form.get("video_loc")
        video = video_file_id_mapping(video_location=video_loc)
        db.session.add(video)
        video_id = table_total_count(video_file_id_mapping)
        print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
        update_video_file_id_mapping(video_loc, video_id)
        db.session.commit()
        logging.info("  >>> given video saved to db: {}".format(video))
        video = "F:\\capstone\\data\\videos\\input\\File_002.mov"


        #extract frames
        frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
        # TODO
        frame_extract_location_current_pickle = generate_result_folder_for_pickle(video_id)

        frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
                                                         "F:\\capstone\\data\\videos\\input","File_002",".mov")
        print("  >>> frames extracted.")
        # save frames to db
        video_plain_framelist_to_db(video_id, frame_list)
        print("video id {}and frame listi is {}".format(video_id, frame_list))
        print("  >>> save frames to db already")
        # save number to db
        insert_pain_video_processed_frame_info(video_id, frame_length)
        print("  >>> save total number to db")
    print("  > finished upload")

    # TODO: upload video, slice to frames and update the db
    return render_template("home.html"), status.HTTP_200_OK
    # return "Hello World!"

if __name__ == "__main__":
    # app.run(host= '0.0.0.0', debug=True)
    app.run(debug=True)