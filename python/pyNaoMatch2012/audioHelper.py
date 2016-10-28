#-*- coding:utf-8 -*-

import pymedia.audio.acodec as acodec
import pymedia.muxer as muxer
import pymedia.audio.sound as sound
from threading import Thread
class audioHelper(Thread):
  playing=True
  def __init__(self):
    Thread.__init__(self)
  def run(self):
    f = open(self.addr, 'rb' ) 
    data= f.read(10000)
    dm = muxer.Demuxer(self.codec)
    frames = dm.parse(data)
    print len(frames)
    dec = acodec.Decoder(dm.streams[0])
    frame = frames[0]
    r= dec.decode(frame[1])#音频数据在 frame 数组的第二个元素中
    print "sample_rate:%s , channels:%s " % (r.sample_rate,r.channels)
    snd = sound.Output( r.sample_rate, r.channels, sound.AFMT_S16_LE )
    if r:snd.play(r.data)
    while True:
      if not self.playing:break
      data = f.read(512)
      if len(data)>0:
        r = dec.decode( data )
        if r: snd.play( r.data )
      else:
        while snd.isPlaying(): time.sleep( .5 )
        break
  def play(self,addr):
    self.addr=addr
    self.codec=addr.split('.')[-1] #suffix
    self.start()
  def stop(self):
    self.playing=False
    pass
if __name__ == '__main__':
  ah=audioHelper()
  ah.play("d:\music.mp3")
  import time
  time.sleep(10)
  ah.stop()
  print "end."