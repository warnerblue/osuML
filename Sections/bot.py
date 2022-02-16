from threading import Thread, Lock

class Bot:

    # Constructor to start thread lock
    def __init__(self):
        # Creates a thread and locks it
        self.lock = Lock()

    # Thread properties
    stopped = True
    lock = None
    points = None

    def update_points(self, points):
        self.lock.acquire()
        self.points = points
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    # Stops this thread.
    def stop(self):
        self.stopped = True

    # Our loop function for this thread.
    def run(self):
        while not self.stopped:
            if not self.points is None:
                points = self.points
                if len(points) > 0:
                    print(list(points))
                # This locks the thread so we can update our results. If we dont do this we could run into errors.
                self.lock.acquire()
                self.lock.release()