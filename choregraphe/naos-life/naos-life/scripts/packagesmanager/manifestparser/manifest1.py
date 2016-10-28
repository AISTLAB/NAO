
class Manifest1(object):
    def __init__(self, id, behavior_name, tree, internals):
        self.name = behavior_name
        self.internals = internals

        self.notes = {}
        self.nature = None
        self.language = None
        self.resources = []
        self.has_loaded = False
        self.loading_sentences = []
        self.trigger_sentences = []
        self.start_positions = []
        self.running_positions = []
        self.stop_positions = []
        self._locals = {}

        try:
            self._loadXML(tree)
        except Exception as e:
            print "Error: %s on %s" % (str(e), self.name)

    def _loadNecessary(self, tree):
        LOADERS = {
            "resources/resource": self.resources.append,
            "positions/start": self.start_positions.append,
            "positions/running": self.running_positions.append,
            "positions/stop": self.stop_positions.append,
        }

        for node in list(tree):
            if tree.tag == "resource":
                pass

    def _loadNotes(self, tree):
        pass

    def _loadLocal(self, tree):
        pass

    def _loadLocals(self, tree):
        for t in list(tree):
            l = t.lower()
            if l in self._locals:
                print "Locals defined 2 times"

            self._locals[l] = self._loadLocal(t)
            if l == self.internals.language.lower():
                self.language = l
                self.local = self._locals[l]

    def _loadXML(self, tree):
        self.nature = tree.find("nature").text.strip()

        necessary = tree.find("necessary")
        notes = tree.find("notes")
        locs = tree.find("locals")

        if necessary is not None:
            self._loadNecessary(necessary)

        if notes is not None:
            self._loadNotes(notes)

        if locs is not None:
            self.loadLocals(locs)

        self.has_loaded = True
