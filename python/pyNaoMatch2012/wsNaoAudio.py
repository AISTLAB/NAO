# -*- coding: utf-8 -*-
#语音模块库
#winxos 2012-07-13
from naoqi import ALProxy
import math,time,almath

class wsNaoAudio:
  _robotip=""
  _audio=None
  _speech=None
  def __init__(self,ip="192.168.143.101"):
    self._robotip=ip
    self._audio=ALProxy("ALAudioPlayer",self._robotip,9559)
    self._speech=ALProxy("ALTextToSpeech",self._robotip, 9559)
    pass
  def say(self,s):
    self._speech.post.say(s)
  def setVolume(self,n):
    if n>1.0:n=1
    if n<0.0:n=0
    self._speech.setVolume(n)
  def setLanguage(self,l):
    pass
  def playMusic(self,s):
    self._audio.post.playFile(s)
  def stopMusic(self):
    self._audio.stopAll()
if __name__ == '__main__':
  ws=wsNaoAudio()
  ws.stopMusic()
  ws.say("hello nice to see you.")
  print "end."