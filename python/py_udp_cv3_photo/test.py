class MyClass(GeneratedClass):

    def __init__(self):
        GeneratedClass.__init__(self)

    def onLoad(self):
        # put initialization code here
        self.cam = ALProxy("ALVideoDevice")

        self.cam.setParam(
            vision_definitions.kCameraSelectID, self.getParameter("camid"))
        old_id = self.cam.getSubscribers()
        for i in old_id:
            self.cam.unsubscribe(i)
        colorSpace = vision_definitions.kRGBColorSpace
        self.nameId = self.cam.subscribe("wscam", getattr(
            vision_definitions, self.getParameter("resolution")), colorSpace, 30)

    def onUnload(self):
        # put clean-up code here

    def onInput_onStart(self):
        self.onStopped()  # activate the output of the box
        self.cam.setParam(
            vision_definitions.kCameraSelectID, self.getParameter("camid"))
        old_id = self.cam.getSubscribers()
        for i in old_id:
            self.cam.unsubscribe(i)
        colorSpace = vision_definitions.kRGBColorSpace
        self.nameId = self.cam.subscribe("wscam", getattr(
            vision_definitions, self.getParameter("resolution")), colorSpace, 30)

    def onInput_onStop(self):
        # it is recommended to reuse the clean-up as the box is stopped
        self.onUnload()
        self.onStopped()  # activate the output of the box

    def onInput_update_img(self):
        print("update")
        raw = self.cam.getImageRemote(self.nameId)
        self.img(raw)
