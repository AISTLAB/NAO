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
from naoqi import ALProxy
import vision_definitions

DEBUG = False
MAX_PACK_SIZE = 1024
port = 9100
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # DGRAM -> UDP
print(platform.platform()[0:5])
if platform.platform()[0:5] == "Linux":
    import fcntl
    ip = socket.inet_ntoa(
        fcntl.ioctl(server.fileno(), 0X8915, struct.pack('256s', 'eth0'[:15]))[20:24])
    print(ip)
    # server.settimeout(10)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
else:
    server.bind(('192.168.1.2', port))
print(server)
_videoProxy = ALProxy("ALVideoDevice", "localhost", 9559)
print(_videoProxy)
resolution = vision_definitions.kQVGA  # 320 * 240
colorSpace = vision_definitions.kRGBColorSpace
_imgClient = None
try:  # 如果已经注册需要先释放
    _imgClient = _videoProxy.subscribeCamera("vm",0, resolution, colorSpace, 15)
except Exception,e:
	print(e)
    #_videoProxy.unsubscribeAllInstances("vm")
    #_imgClient = self._videoProxy.subscribe("vm", resolution, colorSpace, 15)
print(_imgClient)
data = _videoProxy.getImageLocal(_imgClient)
dd = np.fromstring(data[6], dtype=np.uint8)
print(dd)
