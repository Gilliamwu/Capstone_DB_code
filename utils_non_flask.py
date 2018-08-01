from settings import frame_extract_directory, result_saving_directory
import pickle
import os

# for darknet
def unpack_to_dict(tup):
    label, p, rect = tup
    x, y, w, h = rect
    return {'x': x, 'y': y, 'w': w, 'h': h, 'p': p}

# pickle file
def generate_result_folder_for_pickle(video_id):
    dst = result_saving_directory + "/" + str(video_id)
    if not os.path.exists(dst):
        os.mkdir(dst)
    return dst

def pickle_save_to_file(file_f, file_name, data, file_ext='.pkl'):
    file = file_f+"/"+file_name+file_ext
    with open(file,'wb') as f:
        pickle.dump(data, f)
    return file

def pickle_read_file(file_f, file_name, file_ext='.pkl'):
    file = file_f + "/" + file_name + file_ext
    with open(file,'rb') as f:
        data = pickle.load(f)
    return data

def pickle_read_file_direct(file):
    with open(file,'rb') as f:
        data = pickle.load(f)
    return data
