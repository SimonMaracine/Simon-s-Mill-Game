import time
from src.helpers import create_thread


class Timer:
    """Threaded timer object."""

    def __init__(self, count: int):
        self._COUNT = count
        self._time = self._COUNT
        self.ticking = False
        self.thread = None

    def get_time(self) -> int:
        return self._time

    def _run(self):
        while self.ticking:
            self._tick()
            if self._time < 0:
                self.stop()
            time.sleep(0.99999)

    def _tick(self):
        self._time -= 1

    def start(self):
        if not self.ticking:
            self.ticking = True
            self.restart()
            self.thread = create_thread(target=self._run)
            self.thread.start()
        else:
            print("Timer already running.")

    def stop(self):
        self.ticking = False

    def restart(self):
        self._time = self._COUNT
