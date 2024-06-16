from threading import Thread
import cv2

class FileVideoStream:
    def __init__(self, source):
        self.capture = cv2.VideoCapture(source)
        self.stopped = False
        self.frame = None
        self.ret = False

    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            self.ret, self.frame = self.capture.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True

    def more(self):
        return self.ret
