import logging
from threading import Thread
from time import sleep

from deepdream.jobs_queue import DreamQueue, DreamJob

log = logging.Logger("__name__")


class DreamerThread(Thread):

    def __init__(self):
        super().__init__()
        self._queue: DreamQueue = DreamQueue.get_instance()
        self.current_job: DreamJob or None = None
        self.dead = False

    def do_current_job(self):
        if not self.current_job.iterate():
            self.current_job.notify()
            self.current_job = None
        sleep(5)

    def get_new_job(self):
        if self._queue.is_empty():
            sleep(1)
            return
        self.current_job = self._queue.take_job()

    def run(self):
        while True:
            if self.dead:
                return
            try:
                if self.current_job:
                    self.do_current_job()
                else:
                    self.get_new_job()
            except Exception as e:
                # log.error(f"Error in DreamerThread: {e}")
                # self.current_job = None
                # sleep(10)
                raise e

    def kill(self):
        self.dead = True
