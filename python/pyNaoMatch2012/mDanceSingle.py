# -*- coding: utf-8 -*-
#单人舞程序
#使用时请将ip改成需要连接的机器人
#winxos 2012-07-14
import time,math
import wsNaoMotion as wsnm
import audioHelper as ah
if __name__ == '__main__':
  nm=wsnm.wsNaoMotion("192.168.1.102")

  time.sleep(1)
  nm.runBehavior("dance")
  
  ah=ah.audioHelper()
  ah.play("music201207.mp3")
  time.sleep(200)
  ah.stop()