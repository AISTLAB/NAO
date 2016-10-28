#! /usr/bin/python2.7
# coding=utf-8

VALUE_APPEND = 5            # when adding the element
VALUE_REMOVE = -4           # when removing the element
VALUE_LIST_PRESENT = 1      # when the element is present during a step
VALUE_LIST_ABSENT = 0       # when the element is absent during a step

class ContinuityManager(object):
    """
Handle a continuity filter of additions and removals within a list.
Used to avoid oscillations and border effects.
    """
    def __init__(self, threshold=.5, method_type="mean", memory_length=5):
        """
Construct the continuity manager.

    @param threshold the threshold value used in the filter (default is 0.5).
    @param method_type the method value, "mean" (by default) or "median".
    @param memory_length the number of step to be kept in memory.
        """
        self._filter = {}
        self._list_raw = []
        self._threshold = float(threshold)

        if method_type == "median":
            self._method = self._thresholdMedian
        else:
            self._method = self._thresholdMean

        self._memory_length = memory_length

    def _filter_update(self, element, delta):
        """
Update the filter data.

    @param element the modified element.
    @param delta the value to represent the current update.
        """
        if not element in self._filter:
            self._filter[element] = []

        self._filter[element].insert(0, delta)

        if len(self._filter[element]) > self._memory_length:
            self._filter[element].pop()

    def append(self, element):

        if not element in self._list_raw:
            self._list_raw.append(element)
        self._filter_update(element, VALUE_APPEND)

    def remove(self, element):

        if element in self._list_raw:
            self._list_raw.remove(element)
        self._filter_update(element, VALUE_REMOVE)

    def update(self, element_list):
        """
Automatically call 'add' and 'remove' methods to match the
given element_list.

    @return the filtered list using getListFiltered.
        """
        d = self.list_diff(self._list_raw, element_list)

        for element in d["added"]:
            self.append(element)

        for element in d["removed"]:
            self.remove(element)

    @staticmethod
    def list_diff(list1, list2):
        """
    Compute the differences between list1 and list2.

        @param list1 The starting list.
        @param list2 The resulting list.

        @return A dict d = {"added": [item1],
                            "removed": [item3],
                            "unchanged":[]}.
        """
        added = filter(lambda x : x not in list1, list2)
        removed = filter(lambda x : x not in list2, list1)
        unchanged = filter(lambda x : x in list2, list1)

        return {"added": added, "removed": removed, "unchanged": unchanged}

    def step(self):
        """
Update the filter data in order to simulate a time-step.
        """
        #for item in self._filter:
        #    if item in self._list_raw:
        #        self._filter[item] = max(1, self._filter[item] - 1)
        #    else:
        #        self._filter[item] /= 2.0

        for (item, value) in self._filter.items():
            if item in self._list_raw:
                value.insert(0, VALUE_LIST_PRESENT)
            else:
                value.insert(0, VALUE_LIST_ABSENT)

            if (len(value) > self._memory_length):
                value.pop()

    def getListFiltered(self):
        """
    @return The list of elements filtered through the continuity manager.
        """
        #return [item for (item, value) in self._filter.items() if value >= 1]
        return self._method()

    def _thresholdMedian(self):
        """
Apply a median threshold on the filter list.
        """
        ls = []
        for (key, value) in self._filter.items():
            if value.count(1) >= value.count(0) * self._threshold:
                ls.append(key)

        return ls


    def _thresholdMean(self):
        """
Apply a mean threshold on the filter list.
        """
        ls = []
        for (key, value) in self._filter.items():
            if (sum(value) / float(len(value))) >= self._threshold:
                ls.append(key)

        return ls

    def __unicode__(self):
        s = u""

        for (key, value) in self._filter.items():
            s += unicode(key) + u": " + unicode(value) + u"\n"

        s += u"Keeped: "
        for item in self.getListFiltered():
            s += unicode(item) + u" - "

        return s

    def __str__(self):
        return self.__unicode__().encode("utf-8")

def main(args):
    import random

    cm = ContinuityManager()

    a = "a"
    b = "b"
    c = "c"

    print "Add a, b, c"
    cm.update([a, b, c])
    print cm

    print "Step"
    cm.step()
    print cm

    for i in range(10):
        fct = random.choice([("Add", cm.append), ("Remove", cm.remove)])
        item = random.choice((("a", a), ("b", b), ("c", c)))

        print "=" * 10, fct[0], item[0]
        fct[1](item[1])

        print "=" * 5, "Step"
        cm.step()
        print cm

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
