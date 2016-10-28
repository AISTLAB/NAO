#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys
import os
import packagedata
reload(packagedata)
from naoqi import ALProxy, ALModule

ALPackagesManager = None

PackageData = packagedata.PackageData

class PyALPackagesManager(ALModule):
    """
PackagesManager class.
    """
    def __init__(self, behaviors_directory, internals):
        ALModule.__init__(self, "ALPackagesManager")
        self._almemory = ALProxy("ALMemory")
        self._root_folder = behaviors_directory
        self._internals = internals

        self._packages_list = []

        self.update()
        
        try:
            self._almemory.subscribeToEvent("Store/ApplicationInstalled", self.getName(), "onApplicationInstalled")
            self._almemory.subscribeToEvent("Store/ApplicationUninstalled", self.getName(), "onApplicationUninstalled")
            self._almemory.subscribeToEvent("Store/ApplicationUpdated", self.getName(), "onApplicationUpdated")
        except Exception as e:
            ALProxy("ALLogger").error("PackagesManager", "Failed to subscribe to events")

    def __del__(self):
        self._almemory.unsubscribeToEvent("Store/ApplicationInstalled", self.getName())
        self._almemory.unsubscribeToEvent("Store/ApplicationUninstalled", self.getName())
        self._almemory.unsubscribeToEvent("Store/ApplicationUpdated", self.getName())
                
    def _getPackageData(self, name):
        """
_getPackageData.
        """
        return PackageData(self._root_folder, name, self._internals)

    def update(self):
        """
update.
        """        
        packages_list = []

        for l in os.listdir(self._root_folder):
            p = os.path.join(self._root_folder, l)

            if os.path.isdir(p):
                try:
                    packages_list.append(self._getPackageData(l))
                except Exception as e:
                    print "Error when loading: %s - %s" % (l, str(e))

        self._packages_list = packages_list

    def updatePackage(self, name):
        """
updatePackage.
        """
        #Package already present
        for p in self._packages_list:
            if p.name == name:
                p.update()
                return True

        #Added package
        l = os.path.join(self._root_folder, name)

        if os.path.isdir(l):
            self._packages_list.append(self._getPackageData(name))
            return True
        else:
            return False

    def removePackage(self, name):
        """
removePackage.
        """        
        name = name.strip()
        found = None

        for p in self._packages_list:
            if p.name.strip() == name:
                found = p
                break

        if found is not None:
            self._packages_list.remove(found)
            return True
        else:
            return False

    def getBehaviors(self, nature):
        """
getBehaviors.
        """        
        r = []
        for b in self._packages_list:
            r.extend(b.getBehaviors(nature))

        return r

    def getBehavior(self, package_name, name):
        """
getBehavior.
        """        
        r = None
        for b in self._packages_list:
            if (b.name == package_name):
                r = b.getBehavior(name)

        return r

    def onApplicationInstalled(self, pDataName, pValue, pMessage):
    #def onApplicationInstalled(self, pDataName, pValue):
        """
onApplicationInstalled.
        """        
        #ALProxy("ALLogger").info("PackagesManager", "onAppInstalled" + str(pValue))
        self.updatePackage(str(pValue))

    def onApplicationUninstalled(self, pDataName, pValue, pMessage):
    #def onApplicationUninstalled(self, pDataName, pValue):
        """
onApplicationUninstalled.
        """        
        #ALProxy("ALLogger").info("PackagesManager", "onAppUninstalled" + str(pValue))
        self.removePackage(str(pValue))

    def onApplicationUpdated(self, pDataName, pValue, pMessage):
    #def onApplicationUpdated(self, pDataName, pValue):
        """
onApplicationUpdated.
        """
        #ALProxy("ALLogger").info("PackagesManager", "onAppUpdated" + str(pValue))
        self.updatePackage(str(pValue))

    @staticmethod
    def instanciateModule(behaviors_directory, internals):
        """
Instanciate the module in the global variable ALPackagesManager.
        """
        global ALPackagesManager
        if ALPackagesManager is not None:
            raise Exception("Module already exists")
        else:
            ALPackagesManager = PyALPackagesManager(behaviors_directory, internals)

        return ALPackagesManager

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
