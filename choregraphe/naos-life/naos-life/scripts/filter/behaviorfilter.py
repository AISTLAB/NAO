#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import copy
import random
import time

import continuitymanager
reload(continuitymanager)


class BehaviorFilter(object):
    def process(self, behaviors):
        raise Exception("Process function not overloaded")

class BehaviorFilterExcitation(BehaviorFilter):
    def __init__(self, alproxy, deviation):
        self.memory = alproxy("ALMemory")
        self.deviation = deviation

    def process(self, behaviors):
        excitation = float(self.memory.getData("Life/Mood/Excitation"))

        def filter_excitation(x):
            if not "excitation" in x.notes:
                return True

            return x.notes["excitation"].matching(excitation,
                                                  deviation=self.deviation)

        def sorter_excitation(x):
            if not "excitation" in x.notes:
                return float("inf")
            else:
                return ((x.notes["excitation"].value - excitation) ** 2)

        bs = filter(filter_excitation, behaviors)
        bs = sorted(bs, key=sorter_excitation)

        return bs

class BehaviorFilterBattery(BehaviorFilter):
    def __init__(self, proxy):
        self.memory = proxy("ALMemory")

    def process(self, behaviors):
        batt_lvl = int(self.memory.getData("ALSentinel/BatteryLevel"))

        def filter_battery(x):
            if not "battery" in x.notes:
                return True

            return x.notes["battery"].matching(batt_lvl)

        return filter(filter_battery, behaviors)

class BehaviorFilterMemory(BehaviorFilter):
    def __init__(self, proxy):
        self.memory = proxy("ALMemory")

    def process(self, behaviors):
        def filter_memory(x):
            if not "memory" in x.notes:
                return True

            mem = x.notes["memory"]
            try:
                return (str(self.memory.getData(mem.name)) == mem.value)
            except Exception as e: #Value doesn't exists, probably
                return False

        return filter(filter_memory, behaviors)

class BehaviorFilterPeriodicity(BehaviorFilter):
    PERIODICITY_DATA = "Life/%s/LastCall" #TODO: Unify with smartRun value

    def __init__(self, proxy):
        #self.logger = proxy("ALLogger")
        self.memory = proxy("ALMemory")
        self.bm = proxy("ALBehaviorManager")

    def process(self, behaviors):
        runnings = self.bm.getRunningBehaviors()
        has_periodicity = lambda x: ("periodicity" in x.notes and
                                     x.notes["periodicity"] is not None and 
                                     x.notes["periodicity"].value != 0)

        def filter_periodicity(x):
            # Avoid stopping running behaviors
            ## This issue might be solved differently,
            ## (callback on endBehavior ?)
            ## behaviors can be played twice
            ## 
            ## NO! This creates a bug, causing behaviors to run twice in a row, which
            ## completely defeates the purpose of this filter!
            #if x.id in runnings:
            #    self.logger.info("filter_periodicity", str(x.id) + ": RUNNING BEHAVIOR ADDED") 
            #    return True

            # Avoid useless tests
            if not has_periodicity(x):
                #self.logger.info("filter_periodicity", str(x.id) + ": ALLOWING NULL PERIOCIDY") 
                return True                

            # Run the correct tests:
            try:
                call = int(self.memory.getData(self.PERIODICITY_DATA %
                                               x.id))
                delta = (time.time() - call)
            except Exception as inst:
                #TODO: use a Random object with a deterministic seed !
                delta = int(random.random() * x.notes["periodicity"].value)
                call = time.time() - delta
                self.memory.insertData(self.PERIODICITY_DATA % x.id, call)

            result = x.notes["periodicity"].value < delta
            #self.logger.info("filter_periodicity", str(x.id) + ": result: " + str(result))
            return (result)

        return filter(filter_periodicity, behaviors)

class BehaviorFilterFrequency(BehaviorFilter):
    PERIODICITY_DATA = "Life/%s/LastCall" #TODO: Unify with smartRun value

    def __init__(self, proxy):
        self.memory = proxy("ALMemory")

    def process(self, behaviors):
        r = random.random()

        def filter_frequency(x):
            return (("periodicity" not in x.notes) or
                    (x.notes["periodicity"].value in (0, None)) or
                    (10.0/x.notes["periodicity"].value >= r))

        return filter(filter_frequency, behaviors)

class BehaviorFilterContinuity(BehaviorFilter):
    def __init__(self, threshold=.5, method_type="mean"):
        """
    Add a continuity filter upon the behavior list.

    @param threshold the threshold value (default = 0.5).
    @param method_type "mean" or "median" depending on the threshold method.
        """
        self._filter = continuitymanager.ContinuityManager(
                            threshold=threshold,
                            method_type=method_type)

    def process(self, behaviors):
        self._filter.update(behaviors)
        self._filter.step()
        return self._filter.getListFiltered()

RESSOURCES = {
    "All resources": ["All motors", "Leds", "Audio"],
    "All motors": ["Head", "Arms"],
    "Head": ["HeadYawn", "HeadPitch"],
    "Arms": ["Left arm", "Right arm"],
    "Left arm": ["LShoulderPitch", "LShouldeRoll"],
    "Right arm": ["RShoulderPitch", "RShouldeRoll"],
    "Legs": ["LHipYawPitch", "Left Leg", "Right Leg"],
    "Audio": ["Speakers", "Microphones"],
    "Speakers": ["Speech", "Audio player"],
    "Microphones": ["Speech recognition", "Audio recorder"],
}

class BehaviorFilterResources(BehaviorFilter):
    def __init__(self):
        self._available_cur = []
        self._available_init = self.dict_expand(["All resources"])
        self._unknown_used = []

    def dict_expand(self, current):
        result = []
        for c in current:
            if c in RESSOURCES:
                result += self.dict_expand(RESSOURCES[c])
            else:
                result.append(c)

        return result

    def match(self, needed):
        """
        Visit RESSOURCES as a tree
        """
        if needed is None:
            return True

        tested = self.dict_expand(needed)
        to_remove = []
        to_add_unknow = []

        for t in tested:
            #Available resource
            if t in self._available_cur:
                to_remove.append(t)
            #Unknow resources
            elif t not in self._available_init:
                #Unknow never met
                if not t in self._unknown_used:
                    to_add_unknow.append(t)
                #Unknow already used
                else:
                    return False
            else:
                return False

        for t in to_remove:
            self._available_cur.remove(t)
        for t in to_add_unknow:
            self._unknown_used.append(t)

        return True

    def process(self, behaviors):
        self._available_cur = copy.copy(self._available_init)
        self._unknown_used = []
        result = []

        for b in behaviors:
            if not self.match(b.resources):
                continue
            else:
                result.append(b)

        return result

class BehaviorFilterPosition(BehaviorFilter):
    def __init__(self, proxy):
        self.position = proxy("ALRobotPose")
        self.bm = proxy("ALBehaviorManager")

    def process(self, behaviors):
        pos = self.position.getActualPoseAndTime()[0].lower()
        running = self.bm.getRunningBehaviors()

        def filter_position(x):
            """
Check if the given behaviors can be keeped :
    No start position predicate ?
    the current position is in start_positions
    the current position is in authorized position (when standing up,...)
        and the behavior is running.
TODO: if no start positions are given: the behavior can be ran,
      no matter it's position
            """
            return    ((len(x.start_positions) == 0)
                    or (pos in x.start_positions)
                    or ( (pos in x.running_positions or pos == "unknown")
                        and x.id in running))

        return filter(filter_position, behaviors)

class BehaviorFilterTemperature(object):
    THRESHOLD_SIT = 65
    THRESHOLD_ALERT = 75

    THRESHOLD_UNSIT = 60
    THRESHOLD_UNALERT = 70

    STATE_NONE = 0
    STATE_SIT = 1
    STATE_ALERT = 2

    def __init__(self, proxy, debug=False):
        self._memory = proxy("ALMemory")
        self._logger = proxy("ALLogger")
        self._sensors = [
            "LHipPitch",
            "LHipRoll",
            "LHipYawPitch",
            "LKneePitch",
            "RHipPitch",
            "RHipRoll",
            "RKneePitch"
        ]

        self._datas = ["Device/SubDeviceList/" + s +
                       "/Temperature/Sensor/Value" for s in self._sensors]
        self._state = self.STATE_NONE
        self.debug = debug

    def getCurrentValue(self):
        """
        """
        return max(self._memory.getListData(self._datas))

    def process(self, behaviors):

        # Get current temp
        v = self.getCurrentValue()

        def filter_temperature(x):
            if "temperature" in x.notes:
                return x.notes["temperature"].matching(v)
            else:
                return True

        def sorter_temperature(x):
            if not "temperature" in x.notes:
                return float("inf")
            else:
                return ((x.notes["temperature"].value - v) ** 2)

        # Hysteresis/Automaton using a
        # Switch case representation
        if v > self.THRESHOLD_ALERT:
            self._state = self.STATE_ALERT
        elif v < self.THRESHOLD_UNSIT:
            self._state = self.STATE_NONE
        elif self._state == self.STATE_ALERT and v < self.THRESHOLD_UNALERT:
            self._state = self.STATE_SIT
        elif self._state == self.STATE_NONE and v > self.THRESHOLD_SIT:
            self._state = self.STATE_SIT

        # Filter out emergency situations
        if (self._state == self.STATE_NONE or
            self._state == self.STATE_SIT):
            behaviors = filter(filter_temperature, behaviors)
            return sorted(behaviors, key=sorter_temperature)

        elif self._state == self.STATE_ALERT:
            return []

        else:
            1/0

