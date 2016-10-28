# -*- coding: utf-8 -*-
'''
python udp server get remote image.

winxos 2015-07-19
'''
import cv2
import numpy as np
import socket
port=9000
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #DGRAM -> UDP
s.bind(('localhost',port))

datas=""
state=0
img_len=0
while True:
    #接收一个数据
    data,addr=s.recvfrom(1024)
    if state==0:
        if data=="bin":
            state=1
            datas=""
            print("recv binary.")
        if data=="ndarray":
            state=2
            datas=""
            print("recv ndarray")
    elif state==1:
        if data=="end":
            print("transmit done.",img_len,len(datas))
            state=0
            if len(datas)==img_len:
                print("recv ok.")
                img=np.fromstring(datas, dtype='uint8')
                img=cv2.imdecode(img, cv2.IMREAD_COLOR)  
                img=img.reshape((480,640,3))
                cv2.imshow("img",img)
                ch = 0xFF & cv2.waitKey(5)
                if ch == 27:
                    break
            else:
                print("recv err.")
            #break
        else:
            datas +=data
    elif state==2:
        img_len=int(data)
        state=1

            
cv2.destroyAllWindows()
if False: #save
    f=open("tmp.jpeg",'wb')
    f.write(datas)
    f.close()
    print("saved to tmp.jpeg")

