# -*- coding: utf-8 -*-
'''
python udp client
send camera photo to server.
using opencv2 or 3

data convert process:

ndarray multi array -> ndarray single array -> list() -> 
(udp socket) -> 
ndarray dtype uint8 -> reshape -> imshow

winxos 2015-07-19
'''
import cv2
import numpy as np
import socket
import os
import stat  # get file size
import struct  # pack binary

MAX_PACK_SIZE = 1024
DEST_IP = '192.168.1.101'
DEST_PORT = 9000

cam = cv2.VideoCapture(0)

filename = "cat.jpeg"
def send_file(client, filename):
    filesize = os.stat(filename)[stat.ST_SIZE]
    print("%s size: %d Bytes" % (filename, filesize))
    f = open(filename, "rb")
    chList = []
    for i in range(0, filesize):
        (ch,) = struct.unpack("B", f.read(1))
        chList.append(ch)
    client.sendto("bin", (DEST_IP, DEST_PORT))
    packSize = 0
    string = ""
    for i in range(0, filesize):
        packSize = packSize + 1
        string = string + struct.pack("B", chList[i])
        if (MAX_PACK_SIZE == packSize or i == filesize - 1):
            client.sendto(string, (DEST_IP, DEST_PORT))
            packSize = 0
            string = ""
    client.sendto("end", (DEST_IP, DEST_PORT))
def send_cv_img(img):
    client.send("ndarray")
    packSize = 0
    filesize=len(img)
    client.send(str(filesize))
    string = ""
    for i in range(0, filesize):
        packSize = packSize + 1
        string = string +img[i]
        if (MAX_PACK_SIZE == packSize or i == filesize - 1):
            client.send(string)
            packSize = 0
            string = ""
    client.send("end")

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((DEST_IP,DEST_PORT))
print(client)
# client.bind(('',6000))
#send_file(client,filename)

#ret, frame = cam.read()
#a,f=cv2.imencode('.jpg',frame)
#b = cv2.imdecode(f, cv2.IMREAD_COLOR)
#print(type(f),len(f))
#cv2.imshow("1",b)
#print(frame.shape,len(frame))
while True:
    ret, frame = cam.read()
    #cv2.imshow('img', frame)
    #print(frame.size)
    #buf=frame.reshape(921600).tolist()
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),70]
    f,buf=cv2.imencode('.jpg',frame,encode_param)
    buf=np.array(buf)
    buf_data=buf.tostring()
    send_cv_img(buf_data)
    #send_cv_img(buf)
    ch = 0xFF & cv2.waitKey(5)
    if ch == 27:
        break
cv2.destroyAllWindows()
client.close()