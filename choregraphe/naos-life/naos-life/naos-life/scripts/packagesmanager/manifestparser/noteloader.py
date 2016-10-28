#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys

class Note(object):
    def __init__(self, node):
        pass

class NoteDate(Note):
    def __init__(self, node):
        pass

class NoteSimpleValue(Note):
    def __init__(self, node):
        try:
            self.value = node.attrib["value"]
        except:
            raise Exception("NoteSimpleValue without attribute: value")

        try:
            self.value = float(self.value)
        except:
            pass

class NoteNamedValue(Note):
    def __init__(self, node):
        try:
            self.name = node.attrib["id"]
        except:
            raise Exception("NoteNamedValue without attribute: id")

        try:
            self.value = node.attrib["value"]
        except:
            raise Exception("NoteNamedValue without attribute: value")


class NoteRangedValue(Note):
    def __init__(self, node):
        try:
            self.value = float(node.attrib["value"])
        except:
            raise Exception("NoteSimpleValue without attribute: value")

        if "range" in node.attrib:
            self.range = float(node.attrib["range"])
        else:
            self.range = None

    def matching(self, current_value, deviation=None):
        if self.range is not None:
            delta = self.range
        elif deviation is not None:
            delta = deviation
        else:
            delta = 0

        return (abs(current_value - self.value) <= delta)

XML_TO_CLASS = {
    "date": NoteDate,
    "excitation": NoteRangedValue,
    "temperature": NoteRangedValue,
    "battery": NoteRangedValue,
    "periodicity": NoteSimpleValue,
    "memory": NoteNamedValue,
}

def note_load(xml_node):
    if "name" in xml_node.attrib and xml_node.attrib["name"] in XML_TO_CLASS:
        name = xml_node.attrib["name"]
        n = XML_TO_CLASS[name](xml_node)

        return (name, n)

    raise Exception("Unknown node: %s", xml_node.name)

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
