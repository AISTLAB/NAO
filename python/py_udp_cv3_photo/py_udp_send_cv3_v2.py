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
import time


server_ip = '192.168.0.132'
port = 9100

frame_rate = 10
DEBUG = False


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((server_ip, port))
busy = False
from threading import Thread
err_ct = 0
state = 0
is_finished=False

class img_sender(Thread):

    def run(self):
        global busy, err_ct, state
        while not is_finished:
            if not busy:
                client.send("img")
                busy = True
                if DEBUG:
                    print("get img")
                err_ct = 0
            else:
                err_ct += 1
                if DEBUG:
                    print(err_ct)
                if err_ct > 10:
                    busy = False
                    state = 0
            time.sleep(1.0 / frame_rate)

    def __init__(self):
        Thread.__init__(self)


def get_img(ip):
    global busy, state
    IMG_H = 0
    IMG_W = 0
    IMG_Z = 0
    while True:
        # 接收一个数据
        data, addr = client.recvfrom(1024)
        if state == 0:
            if data == "bin":
                state = 1
                datas = ""
                if DEBUG:
                    print("recv binary.")
            if data == "ndarray":
                state = 2
                datas = ""
                if DEBUG:
                    print("recv ndarray")
        elif state == 1:
            if data == "end":
                if DEBUG:
                    print("transmit done.", img_len, len(datas))
                state = 0
                if len(datas) == img_len:
                    busy = False
                    break
                else:
                    if DEBUG:
                        print("recv err.")
            else:
                datas += data
        elif state == 2:
            img_len = 0
            try:
                ds = data.split()
                img_len = int(ds[0])
                IMG_H = int(ds[1])
                IMG_W = int(ds[2])
                IMG_Z = int(ds[3])

            except Exception, e:
                print(e)
            state = 1
    if DEBUG:
        print ("get done", img_len, len(datas), busy)
    img = np.fromstring(datas, dtype='uint8')
    img = cv2.imdecode(img, cv2.IMREAD_COLOR).reshape((IMG_H, IMG_W, IMG_Z))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

g = img_sender()
g.start()
print("running..")
while True:
    img = get_img(server_ip)
    cv2.imshow("img", img)
    ch = 0xFF & cv2.waitKey(5)
    if ch == 27:
        is_finished=True
        break
client.send("exit")
cv2.destroyAllWindows()
time.sleep(1)
client.close()
