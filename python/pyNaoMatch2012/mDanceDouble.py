# -*- coding: utf-8 -*-
#双人舞程序
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-14

import time,math
import wsNaoMotion as wsnm
import audioHelper as ah
from threading import Thread

class dance(Thread):
  nm=None
  def __init__(self,nm):
    Thread.__init__(self)
    self.nm=nm
  def run(self):
    self.nm.runBehavior("dance")

if __name__ == '__main__':
  nm1=wsnm.wsNaoMotion("192.168.1.101")
  nm2=wsnm.wsNaoMotion("192.168.1.102")
  nm1.stiffnessOn()
  nm2.stiffnessOn()
  time.sleep(1)
  nao=dance(nm1)
  big=dance(nm2)
  nao.start()
  big.start()
  
  ah=ah.audioHelper()
  #ah.play("music201207.mp3")
  time.sleep(200)
  ah.stop()