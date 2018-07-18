# server.py

import socket                   # Import socket module
import sys

port = 60000                    # Reserve a port for your service.
# Create a TCP/IP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s = socket.socket()             # Create a socket object


host = socket.gethostname()     # Get local machine name
s.bind(('localhost', port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.

print ('Server listening....')

filename='mytext.txt'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print ('Got connection from', addr)
    data = conn.recv(1024)
    print('Server received', repr(data))


    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       print('Sent ',repr(l))
       l = f.read(1024)
    f.close()

    print('Done sending')
    conn.send(b'Thank you for connecting')
    conn.close()

