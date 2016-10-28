# -*- coding: utf-8 -*-
#找球踢球状态机
#winxos 2012-07-12
import math,time,random
import numpy as np


class state:
    ballLocation=0
    nextstate=None
    def do(self):pass
class findBall(state):
    def do(self,nv,nm):
        print "finding."
        direct=-1
        delta=50
        while True:
            x,y,r=nv._ballImageInfo
            if math.fabs(y-nv.IMGH/2)>delta:
              nm.headRelativePitch(0.2*direct)
              time.sleep(0.5)
              if nm.getHeadPitchAngle()<nm.MIN_HEADPITCH:
                direct=1
              elif nm.getHeadPitchAngle()>nm.MAX_HEADPITCH:
                direct=-1
            else:
                self.ballLocation=0
                if x<140:self.ballLocation=-1
                if x>180:self.ballLocation=1
                break
        print self.ballLocation
        self.__class__=self.nextstate
class approachingBall(state):
    def do(self,nv,nm):
        print "approaching."
        nm._motion.walkInit()
        nm._motion.setWalkArmsEnable(True,True)
        while True:
          x,y,r=nv._ballImageInfo
          if y-nv.IMGH/2>30:
            nm.headRelativePitch(0.05)
          elif y-nv.IMGH/2<-30:
            nm.headRelativePitch(-0.05)
          dx,dy=nv.getGroundBallDistance(nm.getHeadPitchAngle())
          if dy>0:
            if dy<20:
              nm._motion.stopWalk()
              nm.poseInit()
              self.__class__=self.nextstate
              break
            nm._motion.post.setWalkTargetVelocity(0.5,0,-dx*0.5/dy,0.5,[["StepHeight", 0.02]])
          else:
            print "miss."
            break

class prepareKick(state):
    def do(self,nv,nm):
        print "modify."
        nm.poseInit()
        nm.headPitchTo(nm.MAX_HEADPITCH)
        time.sleep(0.5)
        x,y=nv.getGroundBallDistance(nm.getHeadPitchAngle())
        print x,y
        if y>0:
            nm._motion.walkTo((y-10)/100.0,-x/100.0,0,\
            [["MaxStepFrequency", 0.2]])
            if self.ballLocation==0:
                print "mid turn"
                nm._motion.walkTo(0,0,math.radians((random.randint(0,1)*2-1)*20))
            self.__class__=self.nextstate
class findGate(state):
    def do(self,nv,nm):
        "finding gate."
        nm.headPitchTo(nm.MIN_HEADPITCH)
        time.sleep(1)
        x,y,w,h=nv._gateBounding
        print x,w
        if x<5 and w<200:
            nm._motion.walkTo(0,0,math.radians(10))
        elif x>30 and w<200:
            nm._motion.walkTo(0,0,math.radians(-10))
        else:
            self.__class__=self.nextstate
class kickBall(state):
    def do(self,nv,nm):
        print "kicking."
        nm.poseInit()
        nm.headPitchTo(nm.MAX_HEADPITCH)
        time.sleep(1)
        dety=5
        x,y=nv.getGroundBallDistance(nm.getHeadPitchAngle())
        print x,y
        if math.fabs(y-dety)<1 and (math.fabs(x-5)<2 or math.fabs(x+5)<2):
            nm.poseInit()
            nm.kick(x>0)
            self.__class__=self.nextstate
        if y>-1:
            if x>0:
                nm._motion.walkTo((y-dety)/100.0,-x/100.0+0.05,0,\
                [["MaxStepFrequency", 0.1]])
            else:
               nm._motion.walkTo((y-dety)/100.0,-x/100.0-0.05,0,\
                [["MaxStepFrequency", 0.1]])
class finalState(state):
    def do(self,nv,nm):
        nm.hula(2)
        print "successed."

if __name__ == '__main__':
    print "state class"
    


