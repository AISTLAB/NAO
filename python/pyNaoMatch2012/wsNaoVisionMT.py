# -*- coding: utf-8 -*-
#全新的cv2版本框架
#wsNaoVisionMT.py 采用多线程框架进行数据处理
#winxos 2012-07-12

from naoqi import ALProxy
import vision_definitions
import numpy as np
import cv2
import math,time
from threading import Thread

TennisSize=65 #网球实际尺寸
GolfSize=43 #高尔夫球实际尺寸

class wsNaoVision(Thread):
  IMGW=320
  IMGH=240
  _imgClient=None
  _videoProxy=None
  _robotip=""
  _baseSize=TennisSize
  _ball_min = np.array((37,93,126))
  _ball_max = np.array((42,216,248))
  _gate_min=np.array((106,31,195))
  _gate_max=np.array((119,59,232))
  _selection=None
  _ldrag_start = None
  _rdrag_start = None
  _raw=None
  _hsv=None
  _threshBall=None
  _threshGate=None
  hou=None
  _showWindows=False
  _startMonitor=False
  _ballImageInfo=(0,0,0) #图片上最小包裹圆信息
  _ballSpaceDistance=0 #空间球距离
  _gateBounding=(0,0,0,0)
  _nearstObstacleBounding=(0,0,0,0)
  _line=[(0,0),(0,0)]
  def setWindowsOn(self):
    self._showWindows=True

  def startMonitor(self):
    self._startMonitor=True
    self.start()
  def stopMonitor(self):
    self._startMonitor=False
  def run(self):
    if self._showWindows:
      cv2.namedWindow("raw")
      cv2.namedWindow("hsv")
      cv2.namedWindow("ball")
      cv2.namedWindow("gate")
      cv2.setMouseCallback("hsv",self.on_mouse)
    else:
      cv2.destroyAllWindows()
    while self._startMonitor:
      self.getRawImage()
      time.sleep(0.1)
      self.getHSV()
      self._threshBall=self.getROI(self._ball_min,self._ball_max)
      self._threshGate=self.getROI(self._gate_min,self._gate_max)
      gx1,gy1,gw1,gh1=self.getBoundingRectangle(self._threshGate.copy())
      
      self.getLines(self.getROI(self._ball_min,self._ball_max))
      
      self._gateBounding=(gx1,gy1,gw1,gh1)
      gx2,gy2,gw2,gh2=self.getNearstRectangle(self._threshGate)
      self._nearstObstacleBounding=(gx2,gy2,gw2,gh2)
      
      x,y,r=self.getBallImageInfo()
      self._ballImageInfo=(x,y,r)
      self._ballSpaceDistance=self.getSpaceBallDistance()
      
      if self._showWindows:
        cv2.circle(self._raw,(x,y),r,(255,255,0),2)
        cv2.circle(self._raw,(x,y),2,(0,255,255),2)
        cv2.rectangle(self._raw,(gx1,gy1),(gx1+gw1,gy1+gh1),(0,255,0),2)
        cv2.rectangle(self._raw,(gx2,gy2),(gx2+gw2,gy2+gh2),(0,0,255),2)
        cv2.putText(self._raw,"%.2f %.2f %.2f %.2f"%(gx2,gy2,gw2,gh2),\
                    (10,20),cv2.FONT_HERSHEY_PLAIN,1.2,(0,0,255))
        cv2.line(self._raw, self._line[0],self._line[1], (0, 0, 255),2)
        cv2.imshow("raw",self._raw)
        cv2.imshow("hsv",self._hsv)
        cv2.imshow("ball",self._threshBall)
        cv2.imshow("gate",self._threshGate)
        cv2.waitKey(10)
      
  def on_mouse(self,event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self._ldrag_start = (x, y)
    if event == cv2.EVENT_RBUTTONDOWN:
      self._rdrag_start = (x, y)
    if event == cv2.EVENT_LBUTTONUP:
      self._ldrag_start = None
      self._ball_min,self._ball_max=self.getThresh(self._hsv,self._selection)
      print "ball:",self._ball_min,self._ball_max
    if event == cv2.EVENT_RBUTTONUP:
      self._rdrag_start = None
      self._gate_min,self._gate_max=self.getThresh(self._hsv,self._selection)
      print "gate:",self._gate_min,self._gate_max
    if self._ldrag_start:
      xmin = min(x, self._ldrag_start[0])
      ymin = min(y, self._ldrag_start[1])
      xmax = max(x, self._ldrag_start[0])
      ymax = max(y, self._ldrag_start[1])
      self._selection = (xmin, ymin, xmax - xmin, ymax - ymin)
    if self._rdrag_start:
      xmin = min(x, self._rdrag_start[0])
      ymin = min(y, self._rdrag_start[1])
      xmax = max(x, self._rdrag_start[0])
      ymax = max(y, self._rdrag_start[1])
      self._selection = (xmin, ymin, xmax - xmin, ymax - ymin)
  def __init__(self,ip="192.168.143.101"):
    Thread.__init__(self)
    self._robotip=ip
    self.registerImageClient()
    self.switchCam(1)

  def getThresh(self,img,selection): 
    x,y,w,h = selection
    cm=img[y:y+h,x:x+w] #cv2中利用切片和np内置函数来做，快很多
    hsvmin=np.array((np.min(cm[:,:,0]),np.min(cm[:,:,1]),np.min(cm[:,:,2])))
    hsvmax=np.array((np.max(cm[:,:,0]),np.max(cm[:,:,1]),np.max(cm[:,:,2])))
    return hsvmin,hsvmax
  def registerImageClient(self):
    self._videoProxy = ALProxy("ALVideoDevice",self._robotip,9559)
    resolution = vision_definitions.kQVGA  # 320 * 240
    colorSpace = vision_definitions.kRGBColorSpace
    try: #如果已经注册需要先释放
      self._imgClient = self._videoProxy.subscribe("vm", resolution, colorSpace, 15)
    except:
      self._videoProxy.unsubscribeAllInstances("vm") #
      self._imgClient = self._videoProxy.subscribe("vm", resolution, colorSpace, 15) 
  def unRegisterImageClient(self):
    if self._imgClient != None:
      self._videoProxy.unsubscribe(self._imgClient)
  def getBoundingRectangle(self,thresh):
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #找轮廓，会修改原图片
    maxarea=0
    cnt=None
    for h,tcnt in enumerate(contours): #找到面积最大的轮廓
      area = cv2.contourArea(tcnt)
      if area>maxarea:
        maxarea=area
        cnt=tcnt
    (x,y,w,h)=(0,0,0,0)
    if cnt!=None:
      x,y,w,h = cv2.boundingRect(cnt)
    return x,y,w,h
  def getNearstRectangle(self,thresh):
    thresh=cv2.bitwise_not(thresh)
    thresh=cv2.erode(thresh,None)
    thresh=cv2.erode(thresh,None)
    thresh=cv2.erode(thresh,None)
    thresh=cv2.erode(thresh,None)
    
    self._threshGate=thresh.copy()
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #找轮廓，会修改原图片
    nearst=0
    cnt=None
    for h,tcnt in enumerate(contours): #找到最近的轮廓
      x,y,w,h = cv2.boundingRect(tcnt)
      if h<30:continue
      ne=y+h
      if ne>nearst:
        nearst=ne
        cnt=tcnt
    (x,y,w,h)=(0,0,0,0)
    if cnt!=None:
      x,y,w,h = cv2.boundingRect(cnt)
    return x,y,w,h    
  def getMinCircle(self,thresh): #计算最小包裹圆
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #找轮廓，会修改原图片
    maxarea=0
    cnt=None
    for h,tcnt in enumerate(contours): #找到面积最大的轮廓
      area = cv2.contourArea(tcnt)
      if area>maxarea:
        maxarea=area
        cnt=tcnt
    (x,y),r=(0,0),0
    if cnt!=None:
      (x,y),r=cv2.minEnclosingCircle(cnt)
      (x,y),r=(int(x),int(y)),int(r)
    return (x,y),r
  def getLines(self,thresh):
    thresh=cv2.Canny(thresh,50,200)
    thresh=cv2.dilate(thresh,None)
    tmp = cv2.HoughLinesP(thresh, 1, math.pi / 180,100,None,30,10)
    self._line=[(0,0),(0,0)]
    if tmp!=None:
      lines=tmp[0]
      maxdis=0
      cx=0
      for line in lines:
        cx+=line[2]
      cx=cx/len(lines)
      for line in lines:
        if line[2]<cx:continue
        dis=(line[0]-line[2])**2+(line[1]-line[3])**2
        if dis > maxdis:
          maxdis=dis
          x0=line[0]
          y0=line[1]
          x1=line[2]
          y1=line[3]
          self._line=[(x0,y0),(x1,y1)]
      
  def getObjRectangle(self,tmin,tmax):
    return self.getBoundingRectangle(self.getROI(tmin,tmax))
  def getROI(self,tmin,tmax): #普通组合滤波,hsv 格式
    thresh=cv2.inRange(self._hsv, tmin,tmax) #过滤
    thresh=cv2.medianBlur(thresh,3) #中值滤波
    thresh=cv2.GaussianBlur(thresh,(3,3),0) #高斯滤波
    return thresh
  def getRawImage(self): #得到原始图片
    data=self._videoProxy.getImageRemote(self._imgClient) 
    dd=np.fromstring(data[6],dtype=np.uint8)
    self._raw=dd.reshape((data[1],data[0],3)) #三维数组 高,宽,RGB
    self._raw=cv2.cvtColor(self._raw,cv2.COLOR_RGB2BGR) #bgr
  def getRGBRawImage(self): #得到RBG原始图片
    data=self._videoProxy.getImageRemote(self._imgClient) 
    dd=np.fromstring(data[6],dtype=np.uint8)
    return dd.reshape((data[1],data[0],3)) #三维数组 高,宽,RGB
  def getHSV(self):
    #self._hsv=self._raw
    self._hsv=cv2.cvtColor(self._raw,cv2.COLOR_BGR2HSV)
  def setObjSize(self,size): #设置基准大小
    self._baseSize=size
  def getBallImageInfo(self):
    thresh=self._threshBall.copy() #保护
    (x,y),r=self.getMinCircle(thresh)
    return x,y,r
  #pitchang 传入下摄像头角度，计算公式采用下部摄像头,机器人姿态为poseInit时
  def getGroundPointDistance(self,x,y,pitchang):
    xdist=0
    ydist=0
    angle=math.radians(47.64*(y-self.IMGH/2)/self.IMGH+39.7)+0.18+pitchang #上下视角
    h=45+5*math.sin(-pitchang)
    ydist=h/math.tan(angle)
    if ydist<100:ydist-=3 #修正系数，测试出来的数据
    if self._robotip=="192.168.1.103": #两个机器人部分参数不同，修正,nao y值加6cm
      ydist+=5
    wangle=math.radians(60.97*(x-160)/320.0) #左右视角
    xdist=math.sqrt(ydist*ydist+h**2)*math.tan(wangle) #下摄像头高度45+修正值
    xdist=round(xdist,2)
    ydist=round(ydist,2)
    return xdist,ydist
  def getGroundBallDistance(self,pitchang):
    thresh=self._threshBall.copy() #保护
    (x,y),r=self.getMinCircle(thresh)
    xdist=0
    ydist=0    
    if r>3:
      xdist,ydist=self.getGroundPointDistance(x,y,pitchang)
    return xdist,ydist
  def getSpaceBallDistance(self):
    thresh=self._threshBall.copy() #保护
    (x,y),r=self.getMinCircle(thresh)
    dist=0
    if r>0: #缩放转换函数
      dist=round(self._baseSize*0.054/math.atan(math.radians(47.64*r/self.IMGH)),2)
      if dist>50:dist*=1.1
    return dist
  def switchCam(self,cid):
    self._videoProxy.setParam(vision_definitions.kCameraSelectID,cid)
if __name__ == '__main__':
  print "nao vision multi thread class \nwinxos at 2012-07-12"
  import wsNaoMotion as ws
  ip="192.168.1.102"
  m=wsNaoVision(ip)
  m.switchCam(0)
  m.setWindowsOn()
  m.startMonitor()
  
  #mo=ws.wsNaoMotion(ip)
  
  #mo.stiffnessOn()
  #mo.poseInit()
  
  #mo.headPitchTo(mo.MAX_HEADPITCH)
  
  while True:
    #print m.getGroundBallDistance(mo.getHeadPitchAngle())
    time.sleep(0.2)
  
    
  
  



