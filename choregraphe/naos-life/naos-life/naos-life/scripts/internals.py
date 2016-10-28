#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys

class Internals(object):
    def __init__(self, alproxy):
        self.alproxy = alproxy
        self.logger = alproxy("ALLogger")
        self.memory = alproxy("ALMemory")
        self.language = alproxy("ALTextToSpeech").getLanguage().lower()

    def updateLanguage(self, language=None):
        if language is None:
            self.language = self.alproxy("ALTextToSpeech").getLanguage()
        else:
            self.language = language

        self.language = self.language.lower()

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
