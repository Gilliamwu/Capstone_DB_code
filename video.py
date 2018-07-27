import cv2
import os
import time

"""
Here is sample usage:
video_file = "F://term7//CV//ProjectTrail//File_001.mov"
frame_file = "F://term7//CV//ProjectTrail//VideoFrame2"
output_video_loc =  "F://term7//CV//ProjectTrail//File_001_dup.mov"
v = video(video_file)
v.video_to_frames(frame_file)
v.frames_to_video( output_video_loc, input_loc=frame_file) or v.frames_to_video( output_video_loc) directly
"""

class video:
    def __init__(self, video_loc):
        self.video_loc = video_loc
        self.cap = None
        self.video_length = None
        self.fps = None
        self.duration = None
        self.frame_loc = None
        self.frame_format = None
        self.frame_list = []
        self.actual_fram_lens=-1

    def video_to_frames(self, output_loc, output_format="jpg"):
        '''output_loc is a folder. If it doesn't exist we will create one. files will be name from 00001 to XXXXX'''
        self.frame_loc = output_loc
        self.frame_format = output_format
        if not os.path.exists(output_loc):
            os.mkdir(output_loc)

        # Log the time, for stats
        time_start = time.time()
        self.start_cap()
        count = -1
        print("Converting video.. tota\n")
        # Start converting the video
        while self.cap.isOpened():
            count = count + 1
            # Extract the frame
            ret, frame = self.cap.read()
            # Write the results back to output location.
            # If there are no more frames left

            if (count + 1 > self.video_length) or not ret:
                # Log the time again
                time_end = time.time()
                # Release the feed
                self.cap.release()
                # Print stats
                print("Done extracting frames.\n%d total number of frames extracted" % (count+1))
                print("count {}, video_length {}".format(count, self.video_length))
                print("It took %d seconds forconversion." % (time_end - time_start))
                self.actual_fram_lens = count+1
                break

            cv2.imwrite(output_loc + "\\%#05d." % (count) + output_format, frame)
            self.frame_list.append(output_loc + "\\%#05d." % (count) + output_format)

    def get_frame_list(self):
        return self.frame_list

    def get_frame_lengt(self):
        if self.actual_fram_lens != -1:
            return self.actual_fram_lens
        else:
            print(" from cv2, total frames is ")

    def start_cap(self):
        self.cap = cv2.VideoCapture(self.video_loc)
        # Find the number of frames
        self.video_length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 3
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        print(" >> video length {}, fps {}".format(self.video_length, self.fps))

    def frames_to_video(self, output_loc, fps=None, input_loc=None,
                        input_format=None, codec="mp4v",
                        width=None, height=None, debug=False):
        """
        output_loc: locatoin to put movie, please contains extension,
        fps: by default 30, or use what is stored in this class
        input_loc: frame file location, by default is the parameter by another class function video_to_frames
        input_format: format of input images, by default same as parameter passed by video_to_frames
        codec: default mp4v. Availability of codec depends on what has installed by user computer.
            reference of fourcc code http://www.fourcc.org/codecs.php
        width, height: dimension of video, or get from image size
        """
        # Log the time, for stats
        time_start = time.time()

        if input_loc is None:
            input_loc = self.frame_loc

        if fps is None:
            fps = self.fps

        if fps is None:
            if debug:
                print("[INFO] fps not defined from parameter or input. getting fps from origional video")
            self.start_cap()
            self.cap.release()
            fps = self.fps
            if debug:
                print("[INFO] actual fps is {}".format(fps))

        if fps is None and debug:
            print("[ERROR] fps can't be specified. please manually input fps as parameter")

        if (input_loc is None or not os.path.exists(input_loc)) and debug:
            print("[ERROR] frame folder location '{}' doesn't exist".format(input_loc))

        images = []
        if input_format is None:
            print("[INFO] no specificed image file format for input frames. JPG will be used")
            input_format = 'jpg'

        for f in os.listdir(input_loc):
            if f.endswith(input_format):
                images.append(f)

        # Determine the width and height from the first image
        image_path = os.path.join(input_loc, images[0])
        frame = cv2.imread(image_path)
        cv2.imshow('video', frame)
        height, width, channels = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*codec)  # Be sure to use lower case
        out = cv2.VideoWriter(output_loc, fourcc, fps, (width, height))

        print("press q to exit cv2 window")
        for image in images:
            image_path = os.path.join(input_loc, image)
            frame = cv2.imread(image_path)
            if debug:
                print("[INFO] reading {}".format(image))
            out.write(frame)  # Write out frame to video
            cv2.imshow('video', frame)
            if (cv2.waitKey(1) & 0xFF) == ord('q'):  # Hit `q` to exit
                break

        # Release everything if job is finished
        if debug:
            print("[INFO] cleaning up video writer")
        cv2.destroyAllWindows()
        out.release()

        # Log the time again
        time_end = time.time()
        if debug:
            print("It took %d seconds forconversion." % (time_end - time_start))

        print("The output video is {}".format(output_loc))