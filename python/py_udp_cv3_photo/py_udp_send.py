# -*- coding: utf-8 -*-
'''
python udp client send binary file.
winxos 2015-07-19
'''
import socket
import os
import stat  # get file size
import struct  # pack binary
MAX_PACK_SIZE = 1024
DEST_IP = 'localhost'
DEST_PORT = 9000

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

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client.bind(('',6000))
send_file(client,filename)
client.close()