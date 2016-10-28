# -*- coding: utf-8 -*-
#短跑程序
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-14

import time,math
import wsNaoVisionMT as wsnv
import wsNaoMotion as wsnm
import numpy as np

target=np.array([[150,80,70],[180,202,120]])
#target=np.array([[30,15,70],[90,70,140]]) #rgb
if __name__ == '__main__':
  ip="192.168.1.102" #修改此处ip地址为机器人实际连接ip
  
  nv=wsnv.wsNaoVision(ip)
  nv.switchCam(0)
  nm=wsnm.wsNaoMotion(ip)
  nv.setWindowsOn() #显示cv窗口,注销此行将不现实cv窗口
  nv.startMonitor()
  nm.stiffnessOn()
  nv._ball_min=target[0]
  nv._ball_max=target[1]
  nv._gate_min=target[0]
  nv._gate_max=target[1]
  nm.poseInit()
  time.sleep(100)
  while True:
    x,y,w,h=nv._gateBounding
    dx=x+w/2.0-160
    if x==0:dx=0
    print x,w
    nm._motion.post.setWalkTargetVelocity(1.0,0,math.radians(-dx/3.0),1.0,[["MaxStepX", 0.06],["StepHeight", 0.015]])
    if w>170:break
  nm._motion.stopWalk()
  nm.poseInit()
  nv.stopMonitor()