import logging
from threading import Lock
from typing import List

from deepdream.api import DeepDreamAPI, ApiResult
from deepdream.utils import Notifier


log = logging.getLogger()
log.setLevel(logging.INFO)


_QUEUE_LOCK = Lock()


def threadsafe(func):
    def inner(*args, **kwargs):
        _QUEUE_LOCK.acquire(blocking=True)
        result = func(*args, **kwargs)
        _QUEUE_LOCK.release()
        return result
    return inner


class TooManyErrorsException(Exception):
    pass


class DreamJob:

    _MAX_ERRORS: int = 5

    def __init__(self, image: str or bytes, notifier: Notifier, iterations: int, user_data: dict, priority: int):
        """
        :param image: the raw data bytes of the image or the url of said image
        :param notifier: a notifier object used to notify the user of the completion of their deep dream
        :param iterations: the number of dream iterations left to do
        :param user_data: a dictionary containing the user's data, used by the notifier
        :param priority: the job priority, a lower priority will prevail on higher priorities
        """
        self.image: str or bytes = image
        self.notifier: Notifier = notifier
        self.iterations_done: int = 0
        self.iterations_left: int = iterations
        self.user_data: dict = user_data
        self.priority = priority
        self.errors: int = 0

    def dream(self) -> bool:
        """ returns true if the dream was successful, otherwise it returns false """
        api = DeepDreamAPI.get_instance()
        output: ApiResult = api.dream(self.image)
        if output.ok:
            self.image = output.url
            log.info(f"{self.user_data} iteration successful: {self.image} ({self.iterations_left} left)")
            return True
        log.error(f"Error while processing job from {self.user_data}:, message: {output.message}")
        self.errors += 1
        if self.errors == self._MAX_ERRORS:
            raise TooManyErrorsException(
                f"The processing of the current job terminated because there were more than {self._MAX_ERRORS} errors."
            )
        return False

    def iterate(self) -> bool:
        """ returns true if another iteration is needed, otherwise it returns false """
        if self.iterations_left == 0:
            return False
        if self.dream():
            self.iterations_left -= 1
        return True

    def notify(self):
        """ notify user through chosen notifier """
        self.notifier.notify(
            self.user_data,
            {"message": "the processing of your image is done, here's it is:\n\n{}", "image": self.image}
        )

    def __str__(self):
        return f"priority: {self.priority}\n" \
               f"image: {self.image}\n" \
               f"user data: {self.user_data}\n" \
               f"iterations left: {self.iterations_left}\n"


class DreamQueue:

    # Thread safe singleton Queue

    _instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if DreamQueue._instance is not None:
            raise Exception("This class is a singleton!")
        DreamQueue._instance = self
        self._queue: List[DreamJob] = []

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @threadsafe
    def add_job(self, job: DreamJob) -> int:
        for i in range(len(self._queue)):
            if self._queue[i].priority > job.priority:
                self._queue.insert(i, job)
                return i
        self._queue.append(job)
        return 0

    @threadsafe
    def take_job(self) -> DreamJob or None:
        if len(self._queue) == 0:
            return None
        job = self._queue[0]
        self._queue.pop(0)
        return job

    @staticmethod
    def get_instance():
        if DreamQueue._instance is None:
            DreamQueue._instance = DreamQueue()
        return DreamQueue._instance

    def __str__(self):
        result = ""
        for job in self._queue:
            result += f"{str(job)}\n"
        return result


if __name__ == "__main__":
    nn = Notifier()
    job0 = DreamJob("", nn, 10, {}, 10)
    job1 = DreamJob("", nn, 10, {}, 12)
    job2 = DreamJob("", nn, 10, {}, 0)
    job3 = DreamJob("", nn, 10, {}, 3)
    DreamQueue.get_instance().add_job(job0)
    DreamQueue.get_instance().add_job(job1)
    DreamQueue.get_instance().add_job(job2)
    DreamQueue.get_instance().add_job(job3)
    print(DreamQueue.get_instance())
