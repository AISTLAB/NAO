# -*- coding: utf-8 -*-
#状态机实现的点球
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-12
import kickState as state
import kickStateManage
import time,numpy as np
import wsNaoVisionMT as wsnv
import wsNaoMotion as wsnm

ball=np.array([[5,140,140],[20,245,255]])
gate=np.array([[30,130,100],[40,210,220]])

if __name__ == '__main__':
    ip="192.168.1.102" #修改此处ip地址为机器人实际连接ip
    nv=wsnv.wsNaoVision(ip)
    nv.switchCam(1)
    nm=wsnm.wsNaoMotion(ip)
    nv.setWindowsOn() #显示cv窗口,注销此行将不现实cv窗口
    nv.startMonitor()
    nm.stiffnessOn()
    nv._ball_min=ball[0]
    nv._ball_max=ball[1]
    nv._gate_min=gate[0]
    nv._gate_max=gate[1]
    time.sleep(100)
    nm.poseInit()
    c=state.findBall()
    while not isinstance(c,state.finalState):
        c.do(nv,nm)
        time.sleep(0.1)
    c.do(nv,nm)
    print "success."
    time.sleep(1)

    nv.stopMonitor()
 