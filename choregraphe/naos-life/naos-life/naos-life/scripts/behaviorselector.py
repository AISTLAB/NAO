#! /usr/bin/python2.6
# -*- coding: utf-8 -*-

class BehaviorSelector(object):
    def __init__(self,
                 internals,
                 package_handler,
                 filters,
                 nature,
                 debug=False):
        """
Construct a BehaviorSelector.

    @param internals the object with robots internals.
    @param package_handler the package handler proving getBehaviors method.
    @param filter the filte list applied on each list retrieval
    @param nature the nature or list of nature to be retrieven (solitary,
                  interactive,...)
    @param debug Enable debug mode ? (default False)
        """

        self._internal = internals
        self._package_handler = package_handler
        self._filters = filters
        self._nature = nature
        self._debug = debug

        self._logger = internals.logger

        if type(self._nature) is str:
            self._nature = [self._nature]

    def setDebugMode(self, value=True):
        """
set the debug mode to the given value (default is True).
        """
        self._debug = True

    def getBehaviorsList(self):
        b = []
        for n in self._nature:
            b += self._package_handler.getBehaviors(n)
        b = filter(lambda x: x.has_loaded, b)

        for f in self._filters:
            if self._debug:
                self._logger.info("NL", "filter: " + str(f))
                self._logger.info("NL", "<< " + str(b))

            b = f.process(b)

            if self._debug:
                self._logger.info("NL", ">> " + str(b))

        return b

    def __unicode__(self):
        return (u"BehaviorSelector: %i filters" % len(self._filters) +
                u"\n".join(map(lambda x: str(x), self._filters)))

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __repr__(self):
        return "<BehaviorSelector: %i filters>" % len(self._filters)
