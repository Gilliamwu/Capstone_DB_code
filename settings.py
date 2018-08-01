import os
video_saving_directory = "F:/capstone/data/videos/dumped_video"
frame_extract_directory = "F:/capstone/data/videos/extacted_frames"
result_saving_directory = "F:/capstone/data/videos/darknet_output"
weight_file_directory = "backup/yolo-obj_3000.weights"
ubuntu = False

if not os.path.exists(video_saving_directory):
    os.mkdir(video_saving_directory)

if not os.path.exists(frame_extract_directory):
    os.mkdir(frame_extract_directory)

if not os.path.exists(result_saving_directory):
    os.mkdir(frame_extract_directory)

#------mysql updating
MYSQL_SETTINGS = {
    "host": 'localhost',
    "port": 3306,
    "user": "root",
    "passwd": "123456"
}

MYSQL_connection_setting = {
    "port" : 3306,
    "database" : "capstone"
}
