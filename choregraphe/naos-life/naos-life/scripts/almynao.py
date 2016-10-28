#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import time
import sys
import os
path = os.path
from naoqi import ALModule, ALProxy
from xml.etree import ElementTree
import thread

ALMyNao = None

class PyALMyNao(ALModule):
    """
    Synchronize:
        local mynao data,
        remote mynao data,
        local robot configuration (tts.language,...).

    Provide the languageGet/Set,... in order to update
        the remote mynao data within one place.
    """
    def __init__(self):
        ALModule.__init__(self, "ALMyNao")

        # Used proxy
        self._logger = ALProxy("ALLogger")
        self._tts = ALProxy("ALTextToSpeech")
        self._sr = ALProxy("ALSpeechRecognition")
        self._memory = ALProxy("ALMemory")
        self._preferences = ALProxy("ALPreferences")
        self._audiodevice = ALProxy('ALAudioDevice')
        self._audioplayer = ALProxy('ALAudioPlayer')
        self._telepathe = ALProxy("ALTelepathe")
        self._rm = ALProxy("ALResourceManager")
        self._io_lock = thread.allocate_lock()
        
        # The methods to call when setting a local data
        # It might feel kinda lispy but this allows us to make a configuration
        #   as code ersatz easily.
        self._local_autoconf = dict()
        #self._local_autoconf = {
        #    "/nao-life/language": (lambda v:
        #        (bool(self._tts.setLanguage(v)) ^
        #         bool(self._sr.setLanguage(v)))),
        #    "/nao-life/volume": (lambda v:
        #        self._audiodevice.setOutputVolume(int(v)))
        #}
        
        #self._local_autoinit = dict()
        self._local_autoinit = {
            "/nao-life/language": (lambda:
                (self._sr.getLanguage())),
            "/nao-life/volume": (lambda:
                self._audiodevice.getOutputVolume())
        }

        self._local_pref = ["nao-life", "nao-store"]

    	self._tested_folders = ["/home/nao/.config/naoqi/%s",
     	                        "/usr/etc/naoqi/%s",
     	                        "/usr/etc/%s",
     	                        "/usr/preferences/naoqi/%s",
     	                        "/usr/preferences/%s",
     	                        "/etc/naoqi/%s"]

        # Load sound
        # FIXME: Non reliable way of finding the sound!
        sound_path = path.join(path.split(path.abspath(__file__))[0],
                               "..", "sounds", "preferences.wav")
        self._sound_pref = self._audioplayer.loadFile(sound_path)

        # Register to memory updates
        self._memory.subscribeToMicroEvent("/Preferences",
                                           self.getName(),
                                           "",
                                           "prefReceive")
        
        # First data load
        self.__autoinit()
        prefs = self._memory.getData("/Preferences")
        self.__reload_preferences(prefs)
        self.synchronize()
        
    def log(self, message):
        """
@param message the printed message
        """
        self._logger.error("NL", message)

    def exit(self):
        """
destroy the current ALMyNao.
        """
        self._audioplayer.unloadFile(self._sound_pref)
        ALModule.exit(self)

    def prefReceive(self, message, value, key):
        """
Update the local mynao data with the retrieven prefs.
        """
        self.__reload_preferences(value)

    def synchronize(self):
        """
Update the local nao data with the prefs.
(when leaving a behavior that might have changed the local configuration).
        """
        for k in self._local_autoconf:
            try:
                v = self._memory.getData(k)
            except Exception as e:
                self.log("Catched: can't retrieve data: %s - error: %s"
                           % (k, str(e)))
                continue

            try:
                self._local_autoconf[k](v)
            except Exception as e:
                self.log("Catched: Error in autoconf: %s" % str(e))
                continue

    def mynaoGet(self, key):
        """
@param key The key to retrieve
@return The mynao value

Currently this method retrieve the data in almemory, we could
try to update the data from mynao before.
        """
        return self._memory.getData(key)

    def mynaoSet(self, key, value, desc=""):
        """
@param key The key to set.
@param value The value to set.
@param desc The description to set.
        """
        #print "LOCAL"
        self.__local_set(key, value)

        #print "REMOTE"
        try:
            self.__remote_set(key, value, desc)
        except Exception as e:
            self.log("Timeout when setting: %s" % str(e))

    def __autoinit(self):
        """
Load the configuration from the preferences file,
in case there is no internet connection.
        """
        for k in self._local_autoinit:
            self._memory.insertData(k, self._local_autoinit[k]())

        for app in self._local_pref:
            try:
                v = self._preferences.readPrefFile(app, True)
                self._preferences.saveToMemory(v)
            except Exception as e:
                self.log("Catched: Can't load preference: %s, error: %s" %
                            (str(app), str(e)))

    def __remote_set(self, key, value, desc=""):
        """
@param key The key to set
@param value The value

Can raise a TimeoutError if the function takes to long to complete.
        """
        #FIXME: ⋅post of connections might create one thread per remote_set
        if not self._telepathe.isConnected():
            #FIXME: add a timeout instead of a post
            self._telepathe.post.connectNetwork()
            time.sleep(0.2)
        if not self._telepathe.isRPCEnabled():
            #FIXME: add a timeout instead of a post
            self._telepathe.post.enableRPC()
            time.sleep(0.2)

        # Recheck in case our previous post didn't end up well
        if not (self._telepathe.isConnected() and
                self._telepathe.isRPCEnabled()):
            return

        self._telepathe.post.sendRPC("_preferences@xmpp.aldebaran-robotics.com",
                                     "AWPreferences",
                                     "setPreference",
                                     [key, desc, value])

    def __local_set(self, key, value):
        """
When modifying a local pref, set the memory value, raise the event
and call the autoconf function if presents.
        """
        #====== Insert local, avert the rest of the world
        self._memory.insertData(key, value)
        self._memory.raiseMicroEvent(key, value)

        #====== Autoconf local
        if key in self._local_autoconf:
            self._local_autoconf[key](value)

        #====== Update local pref
        try:
            self.__update_local_pref(key, value)
        except Exception as e:
            self.log("Error when updating local pref: %s - %s : %s" %
                     (str(key), str(value), str(e)))

    def __update_local_pref(self, key, value):
        """
This method update the key/value tuple in the correponding xml.
FIXME: Should be remplaced by a simpler ALPref API.
        """
        self._io_lock.acquire()
        splitted = key.split("/")[1:] # "/a/b".split() -> ["", "a", "b"]
        root = splitted[0]
        root_xml = root + ".xml"
        descent = splitted[1:]

        path = None
        #load the local xml
        for p in self._tested_folders:
            if os.path.exists(p % root_xml):
                path = p % root_xml
                break
        if path is None:
            self.log("Path not found for: %s.xml" % root)
            return

        et = ElementTree.ElementTree()
        et.parse(path)

        current = list(et.getroot())[0]
        current_level = "/" + root

        #update the nodes (recursive descent)
        for d in descent:
            current_level += "/" + d
            fct = lambda x: x.attrib["name"] == d
            found = filter(fct, list(current))

            if len(found) == 0:
                current = ElementTree.SubElement(current, "Preference")
                current.set("name", d)
                # current.set("memoryName", current_level)
                current.set("description", "")
                current.set("type", "array")
            else:
                current = found[0]

        #update current
        current.set("type", "string")

        #ElementTree is unable to serialize int by himself...
        if type(value) in (type(42), type(True), type(None)):
            value = str(value).lower()

        current.set("value", value)

        et.write(path)
        self._io_lock.release()

    def __add_memory_names(self, value, prefix):
        """
Legacy preferences load:
    recursive descent on the pref ([mynao [x [y, "desc", value]]]) array.
        """
        for v in value:
            v.append(prefix + '/' + v[0])
            if type(v[2]) == type([]):
                v[2] = self.__add_memory_names(v[2], prefix + '/' + v[0])
            else:
                used_key = "%s/%s" % (prefix, v[0])
                used_value = v[2]
                self.__local_set(used_key, used_value)

        return value

    def __remove_none(self, app):
        """
Remove the None value from app, they cause an error with writePrefFile.
See bug #5876
        """
        for i in range(len(app)):
            if app[i] is None:
                app[i] = "None"
            elif type(app[i]) is type([]):
                app[i] = self.__remove_none(app[i])
            #Else: do nothing, the value is good
        return app

    def __reload_preferences(self, web_preferences):
        """
Legacy preferences load.
        """
        if web_preferences is None:
            return
        preferences = ALProxy('ALPreferences')

        for app in web_preferences:
            try:
                app = self.__remove_none(app) #bug #5876
                preferences.writePrefFile(app[0], [app], False)
                preferences.readPrefFile(app[0], True)
                #preferences.saveToMemory(v)
            except Exception, e:
                self.log("Can't retrieve preferences : %s" % str(e))

        try:
            self.__add_memory_names(web_preferences, '')
        except Exception, e:
            self.log("Error when adding memory names: %s" % str(e))

        #self._rm.waitForResource("Speakers", "ALMyNao", "", 1)
        #if self._rm.areResourcesOwnedBy(["Speakers"], "ALMyNao"):
        self._audioplayer.play(self._sound_pref)
        #    self._rm.releaseResource("Speakers", "ALStore")

    @staticmethod
    def instanciateModule():
        """
Instanciate the module in the global variable ALMyNao.
        """
        global ALMyNao
        if ALMyNao is not None:
            raise Exception("Module already exists")
        else:
            ALMyNao = PyALMyNao()

        return ALMyNao

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
