# -*- coding: utf-8 -*-
#障碍跑
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-14

import time,math
import wsNaoVisionMT as wsnv
import wsNaoMotion as wsnm
import numpy as np
import obstacleState as state

ground=np.array([[0,0,80],[180,220,255]])
if __name__ == '__main__':
  ip="192.168.1.103" #修改此处ip地址为机器人实际连接ip
  
  nv=wsnv.wsNaoVision(ip)
  nm=wsnm.wsNaoMotion(ip)
  nv.switchCam(1)
  nv._gate_min=ground[0]
  nv._gate_max=ground[1] 
  nv.setWindowsOn() #显示cv窗口,注销此行将不现实cv窗口
  nv.startMonitor()
  
  nm.stiffnessOn()
  nm.poseInit()
  nm.headPitchTo(-0.2)
  nm._motion.setWalkArmsEnable(True,True)
  time.sleep(1)
  c=state.findObstacle()
  while not isinstance(c,state.finalState):
      c.do(nv,nm)
      time.sleep(0.1)  
  nv.stopMonitor()


