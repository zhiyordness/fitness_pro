import threading


class LockRenewal:

    def __init__(
            self,
            *,
            lock,
            interval,
    ):
        self.lock = lock
        self.interval = interval
        self.stop_event = threading.Event()
        self.lock_lost_event = threading.Event()
        self.thread = None

    def _run(self):
        while not self.stop_event.wait(self.interval):
            if not self.lock.renew():
                self.lock_lost_event.set()
                break

    def start(self):
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join()