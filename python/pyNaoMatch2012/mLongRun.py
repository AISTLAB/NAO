# -*- coding: utf-8 -*-
#长跑程序
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-14

import time,math
import wsNaoVisionMT as wsnv
import wsNaoMotion as wsnm
import numpy as np


target=np.array([[30,100,152],[37,211,213]])
def getLineInfo(p1,p2):
  t=0
  if p1[1]!=p2[1]:
    t=(p1[0]-p2[0])/float(p1[1]-p2[1])
  if math.fabs(t)<0.1:t=0
  return math.sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2),t
if __name__ == '__main__':
  ip="192.168.1.102" #修改此处ip地址为机器人实际连接ip
  
  nv=wsnv.wsNaoVision(ip)
  nv.switchCam(1)
  nv.setWindowsOn() #显示cv窗口,注销此行将不现实cv窗口
  nv.startMonitor()
  nv._ball_min=target[0]
  nv._ball_max=target[1]
  
  nm=wsnm.wsNaoMotion(ip)
  nm.stiffnessOn()
  nm.poseInit()
  nm.headPitchTo(0.15)
  time.sleep(1)
  while True:
    l=nv._line
    
    le,t= getLineInfo(l[0],l[1])
    print l,le,t
    x,y,r=nv._ballImageInfo
    if math.fabs(t)<0.2 and le>120:
      nm._motion.post.setWalkTargetVelocity(1.0,0,-t/4.0,0.8,[["MaxStepX", 0.06],["StepHeight", 0.015]])
    elif le>50 and math.fabs(t)<1.0:
      nm._motion.post.setWalkTargetVelocity(0.8,0,0.20,0.6)
    else:
      dx=x-160
      nm._motion.post.setWalkTargetVelocity(0.5,0,math.radians(-dx/4.0),0.5,[["MaxStepX", 0.03],["StepHeight", 0.015]])
    time.sleep(1)
    if x==0 and y==0:
      break
  nm._motion.stopWalk()
  nm.poseInit()
  nv.stopMonitor()
