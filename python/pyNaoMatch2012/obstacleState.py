# -*- coding: utf-8 -*-
#障碍跑状态机
#winxos 2012-07-16
import math,time,random
import numpy as np

class state:
    obstacleLocation=0
    turn=1
    nextstate=None
    def do(self):pass
class findObstacle(state):
    def do(self,nv,nm):
        print "finding."
        dx=dy=0
        while True:
            x,y,w,h=nv._nearstObstacleBounding
            zx=x
            if self.turn==-1:zx=x+w
            dx,dy=nv.getGroundPointDistance(zx,y+h,nm.getHeadPitchAngle())
            print dx,dy
            nm._motion.post.setWalkTargetVelocity(0.4,0,-dx*0.5/dy,0.2)
            time.sleep(1)
            if dy<30:
                nm._motion.stopWalk()
                break
        self.__class__=approachingObstacle
class approachingObstacle(state):
    def do(self,nv,nm):
        print "approaching."
        while True:
            nm._motion.post.setWalkTargetVelocity(0.2,0,0.2*self.turn,0.1)
            x,y,w,h=nv._nearstObstacleBounding
            if w<50:
                print "break"
                nm._motion.stopWalk()
                break
        nm._motion.walkTo(0.4,0.1*self.turn,0,[["MaxStepFrequency", 0.4]])
        if self.turn==1:
            nm._motion.walkTo(0.0,0,-0.5*self.turn,[["MaxStepFrequency", 0.1]])
        nm._motion.walkTo(0.4,0,0,[["MaxStepFrequency", 0.1]])
        while True:
            x,y,w,h=nv._nearstObstacleBounding
            zx=x
            if self.turn==-1:zx=x+w
            dx,dy=nv.getGroundPointDistance(zx,y+h,nm.getHeadPitchAngle())
            print dx,dy
        #转弯走
        nm._motion.walkTo(0.6,0,-0.6*self.turn,\
            [["MaxStepFrequency", 0.1]])
        #直走过障碍
        nm._motion.walkTo(0.3,0,0,\
            [["MaxStepFrequency", 0.2]])
        #绕过障碍
        nm._motion.walkTo(0.3,0,-0.6*self.turn,\
            [["MaxStepFrequency", 0.2]])
        nm._motion.walkTo(0.0,0,0.4*self.turn,\
            [["MaxStepFrequency", 0.2]])
        while True:
            x,y,w,h=nv._nearstObstacleBounding
            dx,dy=nv.getGroundPointDistance(x,y+h,nm.getHeadPitchAngle())
        
        self.__class__=overObstacle
class overObstacle(state):
    def do(self,nv,nm):
        print "modify."
        nm.poseInit()
        nm.headPitchTo(nm.MAX_HEADPITCH)
        time.sleep(0.5)
        x,y=nv.getGroundBallDistance(nm.getHeadPitchAngle())
        print x,y
        
class finalState(state):
    def do(self,nv,nm):
        nm.hula(2)
        print "successed."

if __name__ == '__main__':
    print "state class"
    


