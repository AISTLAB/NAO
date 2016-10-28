#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys

class PrefHelper(object):
    def __init__(self, array):
        self.name = array[0]
        self.description = array[1]

        self.value = None
        self.sons = []

        if type(array[2]) is type([]):
            self._load_sons(array[2])
        else:
            self.value = array[2]

    def _load_sons(self, array):
        for s in array:
            self.sons.append(PrefHelper(s))

    def __unicode__(self):
        s = u"prefHelper %s `%s`" % (self.name, self.description)
        return s

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __repr__(self):
        return "<%s>" % str(self)

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
