# -*- coding: utf-8 -*-
#电机控制模块
#winxos 2012-07-11

from naoqi import ALProxy
import motion
import math,time,almath


class wsNaoMotion:
  MAX_HEADPITCH=0.32
  MIN_HEADPITCH=-0.5
  _motion=None
  _behavior=None
  _robotip=""
  def __init__(self,ip="192.168.143.101"):
    self._robotip=ip
    self._motion=ALProxy("ALMotion",self._robotip,9559)
    self._behavior=ALProxy("ALBehaviorManager",self._robotip, 9559)
    
  def getBehaviors(self):
    return self._behavior.getInstalledBehaviors()
  def getRunningBehaviors(self):
    return self._behavior.getRunningBehaviors()
  def runBehavior(self,name):
    if (self._behavior.isBehaviorInstalled(name)):
      if (not self.isBehaviorRunning(name)):
        self._behavior.post.runBehavior(name)
        time.sleep(0.5)
      else:
        print "Behavior is already running."
    else:
      print "Behavior not found."
  def stopBehavior(self):
    pass
  def isBehaviorRunning(self,name):
    return self._behavior.isBehaviorRunning(name)
  def stiffnessOn(self):
    self._motion.stiffnessInterpolation("Body", 1.0, 1.0)
  def stiffnessOff(self):
    self._motion.stiffnessInterpolation("Body", 0.0, 1.0)
  def getAngle(self,jname,sensor=True):
    return self._motion.getAngles(jname,sensor)[0]
  def getHeadPitchAngle(self):
    return self._motion.getAngles('HeadPitch',True)[0]
  def headRelativePitch(self,ang,speed=0.05):
    self._motion.changeAngles('HeadPitch',ang,speed)
  def headPitchTo(self,ang,speed=0.1):
    self._motion.setAngles("HeadPitch", ang,speed)
  def sitDown(self):
    self.runBehavior("sitdown")
  def standUp(self):
    self.runBehavior("standup")
  def hula(self,n,cw=1):
    self.poseInit()
    if cw!=1:cw=-1
# Define the changes relative to the current position
    dx         = 0.07                    # translation axis X (meter)
    dy         = 0.07*cw                    # translation axis Y (meter)
    dwx        = 0.15*cw                    # rotation axis X (rad)
    dwy        = 0.15                    # rotation axis Y (rad)

    # Define a path of two hula hoop loops
    tpath = [ [+dx, 0.0, 0.0,  0.0, -dwy, 0.0],  # point 01 : forward  / bend backward
             [0.0, -dy, 0.0, -dwx,  0.0, 0.0],  # point 02 : right    / bend left
             [-dx, 0.0, 0.0,  0.0,  dwy, 0.0],  # point 03 : backward / bend forward
             [0.0, +dy, 0.0,  dwx,  0.0, 0.0]  # point 04 : left     / bend right
             ] 
    path=[]
    for i in range(n):
      path+=tpath
    timeOneMove  = 0.4 #seconds
    times = []
    for i in range(len(path)):
        times.append( (i+1)*timeOneMove )
    # call the cartesian control API
    effector   = "Torso"
    space      =  motion.SPACE_NAO
    axisMask   = almath.AXIS_MASK_ALL
    isAbsolute = False
    self._motion.positionInterpolation(effector, space, path, axisMask, times, isAbsolute)
    self.poseInit()
  def poseInit(self):
    names = list()
    times = list()
    keys = list()
    
    names.append("HeadYaw")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("HeadPitch")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LShoulderPitch")
    times.append([ 2.00000])
    keys.append([ [ 1.39626, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LShoulderRoll")
    times.append([ 2.00000])
    keys.append([ [ 0.34907, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LElbowYaw")
    times.append([ 2.00000])
    keys.append([ [ -1.39626, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LElbowRoll")
    times.append([ 2.00000])
    keys.append([ [ -1.04720, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LWristYaw")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LHand")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RShoulderPitch")
    times.append([ 2.00000])
    keys.append([ [ 1.39626, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RShoulderRoll")
    times.append([ 2.00000])
    keys.append([ [ -0.34907, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RElbowYaw")
    times.append([ 2.00000])
    keys.append([ [ 1.39626, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RElbowRoll")
    times.append([ 2.00000])
    keys.append([ [ 1.04720, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RWristYaw")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RHand")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LHipYawPitch")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LHipRoll")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LHipPitch")
    times.append([ 2.00000])
    keys.append([ [ -0.43633, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LKneePitch")
    times.append([ 2.00000])
    keys.append([ [ 0.69813, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LAnklePitch")
    times.append([ 2.00000])
    keys.append([ [ -0.34907, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("LAnkleRoll")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RHipRoll")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RHipPitch")
    times.append([ 2.00000])
    keys.append([ [ -0.43633, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RKneePitch")
    times.append([ 2.00000])
    keys.append([ [ 0.69813, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RAnklePitch")
    times.append([ 2.00000])
    keys.append([ [ -0.34907, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    names.append("RAnkleRoll")
    times.append([ 2.00000])
    keys.append([ [ 0.00000, [ 3, -0.66667, 0.00000], [ 3, 0.00000, 0.00000]]])
    
    try:
      self._motion.angleInterpolationBezier(names, times, keys);
    except BaseException, err:
      print err
  def kick(self,rightleg=True):
    if rightleg:
      names = ['RShoulderRoll', 'RShoulderPitch', 'LShoulderRoll', 'LShoulderPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', \
               'RAnklePitch', 'RAnkleRoll', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll']
      angles = [[-0.3], [0.4], [0.5], [1.0], [0.0], [-0.4, -0.2], [0.95, 1.5], [-0.55, -1], [0.2], [0.0], [-0.4], [0.95], [-0.55], [0.2]]
      times =  [[ 0.5], [0.5], [0.5], [0.5], [0.5], [ 0.4,  0.8], [ 0.4, 0.8],  [0.4, 0.8], [0.4], [0.5], [ 0.4], [ 0.4], [ 0.4],  [0.4]]
      self._motion.angleInterpolation(names, angles, times, True)
      
      self._motion.angleInterpolation(['RShoulderPitch', 'RHipPitch', 'RKneePitch', 'RAnklePitch'], 
                                  [1.5,               -0.7,        1.05,         -0.5],  
                                  [[0.15],             [0.15],       [0.15],        [0.15]], True)
      self._motion.angleInterpolation(['RHipPitch', 'RKneePitch', 'RAnklePitch'], \
                                  [-0.5,         1.1,        -0.65], 
                                  [[0.25],       [0.25],     [0.25]], True)
    # kick towards front, left leg    
    else:       
        names = ['LShoulderRoll', 'LShoulderPitch', 'RShoulderRoll', 'RShoulderPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', \
                 'LAnkleRoll', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll']
        angles = [[0.3], [0.4], [-0.5], [1.0], [0.0], [-0.4, -0.2], [0.95, 1.5], [-0.55, -1], [-0.2], [0.0], [-0.4], [0.95], [-0.55], [-0.2]]
        times =  [[0.5], [0.5], [ 0.5], [0.5], [0.5], [ 0.4,  0.8], [ 0.4, 0.8], [ 0.4, 0.8], [ 0.4], [0.5], [ 0.4], [0.4] , [0.4],   [0.4]]        
        self._motion.angleInterpolation(names, angles, times, True)
        self._motion.angleInterpolation(['LShoulderPitch', 'LHipPitch', 'LKneePitch', 'LAnklePitch'],
                                    [1.5,               -0.7,        1.05,         -0.5],        
                                    [[0.15],             [0.15],       [0.15],        [0.15]], True)
        self._motion.angleInterpolation(['LHipPitch', 'LKneePitch', 'LAnklePitch'], 
                                    [-0.5,         1.1,          -0.65], 
                                    [[0.25],      [0.25],        [0.25]], True) 
    self.poseInit()
    
if __name__ == '__main__':
  m=wsNaoMotion()
  m.stiffnessOn()
  m.headPitchTo(0.0)
  time.sleep(1)
  m.headPitchTo(0.3)
  time.sleep(3)
  m.headRelativePitch(-0.1)