import re
from subprocess import Popen, PIPE
import subprocess
import time
from settings import weight_file_directory, ubuntu

import logging
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')


test_str = """
     Total BFLOPS 34.876
     seen 32
    using predict gpudata/test1/12957_1.jpg: Predicted in 0.051701 seconds.
    using do_nms_sortTring to get actual detection
    crack: 54%
    crack: 25%
     >>>coordinate: 161 99 108 178 <<<
     >>>coordinate: 111 125 213 202 <<<
    Not compiled with OpenCV, saving to predictions.png instead"""



def run_yolo_in_cmd(img_name):
    # cmd = "./darknet detector test cfg/obj.data cfg/yolo-obj.cfg %s %s" % (weight_file_directory, img_name)
    # print("cmd is {}\n".format(cmd))
    start_time = time.time()
    # if not ubuntu:
    #     try:
    #         cygwin_pip = Popen("C:/cygwin64/bin/bash.exe", stdin=PIPE, stdout=PIPE)
    #         cygwin_pip.stdin.write(str.encode(cmd))
    #         cygwin_pip.stdin.close()
    #         stdout_result = cygwin_pip.stdout.read()
    #         print(" ==== result is \n{}\n\n".format(stdout_result))
    #     except Exception as e:
    #         stdout_result = test_str
    #         print(" =-------- error running bash")
    #         raise e
    # else:
    #     try:
    #         stdout_result = subprocess.check_output(cmd, shell=True)
    #         print(" ==== result is \n{}\n\n".format(stdout_result))
    #     except Exception as e:
    #         raise e
    stdout_result = test_str
    logging.info(" >>> time for analyzie frame {} is  {}".format(img_name, time.time()-start_time))
    return stdout_result

def get_data_from_console(input_string):
    print(" receiving input string like this : {}".format(input_string))
    if not (isinstance(input_string,str)):
        input_string = input_string.decode("utf-8")

    result = []
    splitted_input = input_string.split("\n")
    if (len(splitted_input) < 4):
        return result
    start_i = -1
    count_t = 0
    for i in range(len(splitted_input)):
        # print(splitted_input[i].strip())
        if re.match(r'>>>coordinate: \d+ \d+ \d+ \d+ <<<', splitted_input[i].strip()):
            count_t += 1
            if start_i == -1:
                start_i = i
    #         print("ahahaha {}".format(i))
    # print("\n\n")
    # print(start_i)
    # print(count_t)

    if start_i == -1  or count_t == 0:
        return result
    else:
        for j in range(start_i,start_i+count_t):
            # to get possibility
            # poss should be in format: "crack: 25%" -> 25
            poss = int(splitted_input[j-count_t].strip().split()[-1][:-1])
            # coor should be in format  ">>>coordinate: 161 99 108 178 <<<" ->
            coor = splitted_input[j].strip().split()[1:-1]
            coor_n = [int(x) for x in coor]
            result.append((b'crack', poss*0.01, (coor_n[0],coor_n[1],coor_n[2],coor_n[3])))
        print("yolo result: {}".format(result))
        return result

if __name__ == "__main__":
    print(get_data_from_console(test_str))