import threading

class SafeThread(threading.Thread):
    def __init__(self, target, *args):
        threading.Thread.__init__(self)
        self.daemon = True
        self.target = target
        self.args = args
        self.stop_ev = threading.Event()

    def stop(self):
        self.stop_ev.set()

    def run(self):
        while not self.stop_ev.is_set():
            self.target(*self.args)
