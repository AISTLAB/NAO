#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys
import os

import behaviordata
reload(behaviordata)

BehaviorData = behaviordata.BehaviorData

class PackageData(object):
    def __init__(self, root_folder, package_name, internals):
        self.name = package_name
        self._root_folder = root_folder
        self._behaviors = []
        self._internals = internals

        self._folder = os.path.join(root_folder, package_name)

        self.update()

    def _getBehaviorData(self, name):
        try:
            return BehaviorData(self._root_folder,
                                self.name,
                                name,
                                self._internals)
        except Exception as inst:
            print >>sys.stderr, "Can't loadt: %s - error: %s" % (name,
                                                                 str(inst))
            return None

    def update(self):
        behaviors = []
        for l in os.listdir(self._folder):
            p = os.path.join(self._folder, l)
            pxml = p + ".xml"

            if os.path.exists(pxml):
                b = self._getBehaviorData(l)
                if b is not None:
                    behaviors.append(b)

        self._behaviors = behaviors

    def getBehaviors(self, nature):
        return filter(lambda x: x.nature == nature, self._behaviors)

    def getBehavior(self, name):
        for b in self._behaviors:
            if b.name == name:
                return b
        return None

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
