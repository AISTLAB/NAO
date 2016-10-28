#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys
import os
import noteloader

def auto_cast(s):
    try:
        if (type(s) == type("s")):
            return unicode(s.strip())
        elif (type(s) == type(u"s")):
            return s.strip()
        else:
            return s
    except:
        return s

class Manifest0(object):
    LANGUAGE_PRIORITY = ["current", "none"]

    def __init__(self, id, behavior_name, tree, internals):
        self.id = id
        self._internals = internals

        self.has_loaded = False
        self.name = behavior_name
        self.nature = u"None"
        self.start_positions = []
        self.running_positions = []
        self.langages = []
        self.resources = []
        self.language = internals.language.lower()
        self.languages = []
        self.trigger_sentences = []
        self.loading_sentences = []
        self.notes = {}

        self._loadXml(tree)

    def _loadXml(self, tree):
        self.start_positions = []
        self.running_position = []
        self.resources = []

        #has loaded
        root = tree
        if root is None:
            self.has_loaded = False
            return False

        #Nature
        node_nature = root.find("nature")
        if node_nature is not None:
            self.nature = auto_cast(node_nature.text.strip())
            if self.nature == "interactive": #Allow "interactive" name for app
                self.nature = "application"

        #Start position and ressources
        resources = root.find("resources")
        if resources is not None:
            if "startposition" in resources.attrib:
                self.start_positions.append(
                    resources.attrib["startposition"].lower())

            for info in list(resources):
                if info.tag.lower() == "positions":
                    for pos in list(info):
                        if pos.tag == "start":
                            self.start_positions.append(auto_cast(pos.text))
                        elif pos.tag == "running":
                            self.running_positions.append(auto_cast(pos.text))
                elif info.tag.lower() in ("resources", "resource"):
                    self.resources.append(auto_cast(info.text))

        self._loadLocals(root)
        self._loadNotes(root)

        self.has_loaded = True

        return True

    def _loadLocals(self, root):

        #Find the right local
        local = None

        #Pick the available language
        xml_locals = root.findall("local")
        if xml_locals is not None:
            self.languages = [n.attrib["language"] for n in xml_locals
                              if "language" in n.attrib]
            self.language = self._internals.language.lower()

        #Pick update language to the one available then the corresponding local
        if len(self.languages) > 0:

            #Update language
            for c in self.LANGUAGE_PRIORITY:
                if c == "current" and self.language in self.languages:
                    break
                elif c == "*":
                    self.language = self.languages[0]
                    break
                elif c in self.languages:
                    self.language = c
                    break

            #Get the corresponding local
            found_locals = root.findall("local")
            for n in found_locals:
                if ("language" in n.attrib and
                    n.attrib["language"].lower() == self.language.lower()):
                    local = n
                    break

        #Full name
        if local is not None:
            n = local.find("name")
            self.name = auto_cast(n.text)

        #Trigger sentences:
        if local is not None:
            trig = local.find("triggers")
            if trig is not None:
                sentences = trig.find("triggerSentences")
                if sentences is not None:
                    self.trigger_sentences = [auto_cast(n.text.strip()) for n
                                              in list(sentences) if n.tag == "sentence"]

        #Loading sentences
        if local is not None:
            lsent = local.find("loadingsentences")
            if lsent is not None:
                self.loading_sentences = [auto_cast(n.text) for n in lsent
                                          if n.tag == "loadingsentence"]

    def _loadNotes(self, root):

        node = root.find("notes")
        if node is None:
            return

        for n in node:
            try:
                (name, obj) = noteloader.note_load(n)
                self.notes[name] = obj
            except Exception as e:
                self._internals.logger.error(
                    "NL",
                    "Error loading note from : %s - %s" % (self.id, str(e))
                )

    def update(self):
        self._loadXML()

    def __unicode__(self):
        return """BehaviorData:\
id: %s
""" % self.id

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __repr__(self):
        return ("<BehaviorData: %s>" % self.id)

    def dynamicSerialize(self):
        return [self.id, self.name] + self.loading_sentences

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
