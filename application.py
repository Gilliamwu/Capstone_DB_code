from flask import request, jsonify, Flask
from flask_api import status
from functools import wraps
from models import db

def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()


#
# import logging
# logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
#
# from utils import split_video_to_frames, \
#     table_total_count, \
#     update_video_file_id_mapping, \
#     video_plain_framelist_to_db, \
#     generate_result_folder_for_frames,\
#     insert_pain_video_processed_frame_info,\
#     update_video_processed_frame_info_total_frames,\
#     db_check_if_vid_exist
#
# from utils_non_flask import generate_result_folder_for_pickle, \
#     pickle_read_file_direct, \
#     unpack_to_dict
#
# application = app = Flask(__name__)
# application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask:p2s5w0rD@flasktest.cfparnusqsew.us-west-2.rds.amazonaws.com/aeolusdb'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/capstone'
# db.app = application
# db.init_app(application)
# import os
# from models import User,video_file_id_mapping, crack_detection_result, video_processed_frame_info
#
#
# # TODO: later rmv--- not really used, for testing only
# from flask import render_template
# from flask import request
#
# first_time = False
# if first_time:
#     admin = User('admin1', 'admin1@example.com')
#     db.create_all()
#     print(" >> first time: all tables created")
#     # db.session.add(admin)
#     db.session.commit()
#     User.query.all()
#     print(" >> first time: test insert value, success")
#
# ###################################################################
# ###################################################################
#
# users = {
#     "a":"b",
#     "Admin1": "admin_password",
#     "User1": "password1"
#     }
#
# def is_valid_user(username, password):
#     return username in users and users[username] == password
#
# def ask_for_login(has_auth):
#     '''
#     Checks for login
#     '''
#     if not has_auth:
#         message = {'message': "Login Required"}
#     else:
#         message = {'message': "Invalid Credentials"}
#
#     resp = jsonify(message)
#     resp.status_code = 401
#     resp.headers['WWW-Authenticate'] = 'Basic realm="AEOLUS Login"'
#     return resp
#
# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth:
#             return ask_for_login(False)
#         elif not is_valid_user(auth.username, auth.password):
#             return ask_for_login(True)
#         return f(*args, **kwargs)
#     return decorated
#
# @application.route("/", methods=['POST'])
# @requires_auth
# def main_auth():
#     return "Hello World!", status.HTTP_200_OK
#
# @application.route("/video", methods=['POST'])
# @requires_auth
# def video_upload():
#     if 'video' in request.files:
#         submitted_file = request.files['video']
#         # your save code goes here
#
#         video_id = table_total_count(video_file_id_mapping)+1
#         output_video_name = "test{}".format(video_id)
#         output_video_ext = ".avi"
#         video_loc = "received_video\\"+output_video_name+output_video_ext
#         submitted_file.save(video_loc)
#
#         video = video_file_id_mapping(video_location=video_loc)
#         db.session.add(video)
#         video_id = table_total_count(video_file_id_mapping)
#         print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
#
#         update_video_file_id_mapping(video_loc, video_id)
#         db.session.commit()
#         logging.info("  >>> given video saved to db: {}".format(video))
#         frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
#         # just to create a pickle folder
#         generate_result_folder_for_pickle(video_id)
#
#         frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
#                                             os.getcwd(), video_loc, ".avi")
#         print("  >>> frames extracted.")
#         # save frames to db
#         video_plain_framelist_to_db(video_id, frame_list)
#         print("video id {}and frame list is {}".format(video_id, frame_list))
#         print("  >>> save frames to db already")
#         # save number to db
#         insert_pain_video_processed_frame_info(video_id, frame_length)
#         print("  >>> save total number to db")
#
#         # data = {'uid': uid, 'frames': n_frames}
#         data = {'uid': video_id, 'frames': frame_length}
#         resp = jsonify(data)
#         resp.status_code = 201
#         return resp
#     else:
#         return "", status.HTTP_400_BAD_REQUEST
#
# @application.route("/video/<string:vid_name>/frames", methods=['GET'])
# @requires_auth
# def video_frame_status_get(vid_name):
#     # check if video in db
#     flag, reason_or_processed_name = db_check_if_vid_exist(vid_name)
#     if flag:
#         target_v_info = video_processed_frame_info.query.filter_by(video_id = reason_or_processed_name).first()
#         n_frames = target_v_info.total_frames
#         completed_frames = target_v_info.processed_frames_n
#         # n_frames = 200
#         # completed_frames = 6 #[1, 2, 3]
#         data = {'frames': n_frames, 'completed_frames': completed_frames}
#         print(" YYYYYYYYY frame data: {}".format(data))
#         resp = jsonify(data)
#         resp.status_code = 200
#         return resp
#     return reason_or_processed_name, status.HTTP_400_BAD_REQUEST
#
# @application.route("/video/<string:vid_name>/frames/<int:frame_index>", methods=['GET'])
# @requires_auth
# def video_frame_get(vid_name, frame_index):
#     flag, reason_or_processed_name = db_check_if_vid_exist(vid_name)
#     if flag:
#     # check if video in db
#         # check if frame processed
#         target_frame_row = crack_detection_result.query.filter_by(video_id=reason_or_processed_name, frame_id = frame_index).first()
#         if target_frame_row.detect_flag == 1:
#             lst_of_tup = pickle_read_file_direct(target_frame_row.result_loc)
#
#             boxes = [unpack_to_dict(t) for t in lst_of_tup]
#
#             # box1 = {'x': 0, 'y': 0, 'w': 1, 'h': 1, 'p': 0.49}
#             # box2 = {'x': 0, 'y': 0, 'w': 1, 'h': 1, 'p': 0.49}
#             # boxes = [box1, box2]
#             data = {'boxes': boxes}
#             resp = jsonify(data)
#             resp.status_code = 200
#             print("  YYYY get data: {}".format(data))
#             return resp
#         # frame not yet processed
#         else:
#             return "Frame not processed yet", status.HTTP_204_NO_CONTENT
#     else:
#         return reason_or_processed_name, status.HTTP_400_BAD_REQUEST
#
# @application.route("/test", methods=['GET'])
# @requires_auth
# def test_video_get():
#     print("============HELLO WORLD the test page")
#     # video_id = 1
#     # frame_list = ["F:\\capstone\\data\\videos\\extacted_frames/0000.jpg",
#     #               "F:\\capstone\\data\\videos\\extacted_frames/00001.jpg",
#     #               "F:\\capstone\\data\\videos\\extacted_frames/00002.jpg",
#     #               "F:\\capstone\\data\\videos\\extacted_frames/00003.jpg",
#     #               "F:\\capstone\\data\\videos\\extacted_frames/00004.jpg"]
#     # frame_frame_length = 5
#     # video_plain_framelist_to_db(video_id, frame_list)
#     return render_template("home.html"), status.HTTP_200_OK
#
# @application.route("/test", methods=['POST'])
# @requires_auth
# def test_video():
#     # video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
#     print("============receive post frmo test page")
#     if request.form:
#         video_loc = request.form.get("video_loc")
#
#         video = video_file_id_mapping(video_location=video_loc)
#         db.session.add(video)
#         video_id = table_total_count(video_file_id_mapping)
#         print("  > received : {}\n > it's video id should be {}".format(video_loc, video_id))
#         update_video_file_id_mapping(video_loc, video_id)
#         db.session.commit()
#         logging.info("  >>> given video saved to db: {}".format(video))
#         video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
#
#         #extract frames
#         frame_extract_location_current_video = generate_result_folder_for_frames(video_id)
#         # TODO
#         frame_extract_location_current_pickle = generate_result_folder_for_pickle(video_id)
#
#         frame_list, frame_length = split_video_to_frames(frame_extract_location_current_video,
#                                                          "F:\\capstone\\data\\videos\\input","File_002",".mov")
#         print("  >>> frames extracted.")
#         # save frames to db
#         video_plain_framelist_to_db(video_id, frame_list)
#         print("video id {}and frame listi is {}".format(video_id, frame_list))
#         print("  >>> save frames to db already")
#         # save number to db
#         insert_pain_video_processed_frame_info(video_id, frame_length)
#         print("  >>> save total number to db")
#     print("  > finished upload")
#
#     # TODO: upload video, slice to frames and update the db
#     return render_template("home.html"), status.HTTP_200_OK
#     # return "Hello World!"
#
# if __name__ == "__main__":
#     # app.run(host= '0.0.0.0', debug=True)
#     application.run(debug=True)