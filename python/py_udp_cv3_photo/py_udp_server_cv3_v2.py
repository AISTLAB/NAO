# -*- coding: utf-8 -*-
'''
python udp server get remote image.

winxos 2015-07-19
'''
import cv2
import numpy as np
import socket
import os
import stat  # get file size
import struct  # pack binary
import platform

DEBUG = False
MAX_PACK_SIZE = 1024
port = 9100
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # DGRAM -> UDP
if platform.platform()[0:5] == "Linux":
    import fcntl
    ip = socket.inet_ntoa(
        fcntl.ioctl(server.fileno(), 0X8915, struct.pack('256s', 'eth0'[:15]))[20:24])
    server.bind((ip, port))
else:
    server.bind(('192.168.0.100', port))


def send_file(filename, addr):
    filesize = os.stat(filename)[stat.ST_SIZE]
    print("%s size: %d Bytes" % (filename, filesize))
    f = open(filename, "rb")
    chList = []
    for i in range(0, filesize):
        (ch,) = struct.unpack("B", f.read(1))
        chList.append(ch)
    server.sendto("bin", addr)
    packSize = 0
    string = ""
    for i in range(0, filesize):
        packSize = packSize + 1
        string = string + struct.pack("B", chList[i])
        if (MAX_PACK_SIZE == packSize or i == filesize - 1):
            server.sendto(string, addr)
            packSize = 0
            string = ""
    server.sendto("end", addr)


def send_cv_img(img, addr):
    server.sendto("ndarray", addr)
    packSize = 0
    filesize = len(img)
    server.sendto(str(filesize), addr)
    string = ""
    for i in range(0, filesize):
        packSize = packSize + 1
        string = string + img[i]
        if (MAX_PACK_SIZE == packSize or i == filesize - 1):
            server.sendto(string, addr)
            packSize = 0
            string = ""
    server.sendto("end", addr)


cam = cv2.VideoCapture(0)

datas = ""
state = 0
img_len = 0
while True:
    ret, frame = cam.read()
    data, addr = server.recvfrom(1024)
    print(data, addr)
    if data == "img":
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # quality
        f, buf = cv2.imencode('.jpg', frame, encode_param)
        buf_data = np.array(buf).tostring()
        send_cv_img(buf_data, addr)
