import utils

import settings

video = "F:\\capstone\\data\\videos\\input\\File_002.mov"
frame_list, frame_length = utils.split_video_to_frames(settings.frame_extract_directory, "F:\\capstone\\data\\videos\\input",
                                                 "File_002", ".mov")
print(frame_list)
print(frame_length)

# # server.py
#
# import socket                   # Import socket module
# import sys
#
# port = 60000                    # Reserve a port for your service.
# # Create a TCP/IP socket
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # s = socket.socket()             # Create a socket object
#
#
# host = socket.gethostname()     # Get local machine name
# s.bind(('localhost', port))            # Bind to the port
# s.listen(5)                     # Now wait for client connection.
#
# print ('Server listening....')
#
# filename='rec.avi'
#
# # with open(filename, "wr") as f:
# while True:
#     conn, addr = s.accept()     # Establish connection with client.
#
#     print('Got connection from', addr)
#     data = conn.recv(1024)
#
#     # f.write(data)
#     print('Server received', repr(data))
#
#     # f.close()
# #
# # f = open(filename,'rb')
# # l = f.read(1024)
# # while (l):
# #    conn.send(l)
# #    print('Sent ',repr(l))
# #    l = f.read(1024)
# # f.close()
#
#     print('Done receiving')
#     conn.send(b'Thank you for connecting')
#     conn.close()
#
