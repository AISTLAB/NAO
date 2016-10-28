# -*- coding: utf-8 -*-
#配置状态衔接过程
#winxos 2012-07-09
import kickState as state
state.findBall.nextstate=state.approachingBall
state.approachingBall.nextstate=state.prepareKick
state.prepareKick.nextstate=state.kickBall
state.findGate.nextstate=state.kickBall
state.kickBall.nextstate=state.finalState




