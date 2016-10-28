# -*- coding: utf-8 -*-
'''
python udp server get binary file.
winxos 2015-07-19
'''
import socket
port=9000
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM) #DGRAM -> UDP
s.bind(('localhost',port))
f=open("tmp.jpeg",'wb')
datas=""
state=0
while True:
    #接收一个数据
    data,addr=s.recvfrom(1024)
    if state==0:
        if data=="bin":
            state=1
            datas=""
            print("recv binary.")
    elif state==1:
        if data=="end":
            print("transmit done.")
            break
        else:
            datas +=data
f.write(datas)
f.close()
print("saved to tmp.jpeg")
