#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
import sys
import os
from xml.etree.ElementTree import ElementTree
import imp
import manifestparser
reload(manifestparser)

print dir(manifestparser)

class BehaviorData(object):
    """
    Dynamic manifest loading class:
        Instanciate a manifestData depending on the xml version.
        Provide REQUIRED_FIELDS in order to validate the new instance.

    How it works:
        The meta class open the xml then looks for its version,
        the manifestparser.version# module is then imported and the
        correponding class instanciated.

    REQUIRED_FIELDS is used in order to check every evolution for the manifest
    are explicitly implemented in olders version (even if it's an empty
    field).

    MANIFESTS: Dict versionName:class
    TODO: Dynamic load from manifestparser folder

    TODO: Cache module loading and required_field checks.
    """
    REQUIRED_FIELDS = [
        "name",
        "notes",
        "nature",
        "languages",
        "resources",
        "has_loaded",
        "loading_sentences",
        "trigger_sentences",
        "start_positions",
        "running_positions",
    ]

    MANIFESTS = {
        "0": manifestparser.Manifest0,
        "1": manifestparser.Manifest1,
    }

    def __new__(cls, root_folder, package_name, behavior_name, internals):
        b_id = "%s/%s" % (package_name, behavior_name)
        xml = os.path.join(root_folder, package_name, behavior_name) + ".xml"
        tree = cls.open_xml(xml)

        #Instanciate the manifest depending on version
        i = cls.get_xml_class(tree)(b_id, behavior_name, tree, internals)

        #Check required fields
        diri = dir(i)
        for f in cls.REQUIRED_FIELDS:
            if not f in diri:
                err =  "Missing Required Field: %s within %s" % (f, str(i))
                Exception(err)

        return i

    @staticmethod
    def open_xml(xml_path):
        em = ElementTree()
        em.parse(xml_path)
        return em.getroot()

    @classmethod
    def get_xml_class(cls, tree):
        version = tree.attrib.get("manifest_version", "0")
        return cls.MANIFESTS[version]

def main(args):
    print >>sys.stderr, "No main defined for this module"
    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
