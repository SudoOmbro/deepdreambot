import logging
from threading import Lock

from deepdream.api import DeepDreamAPI, ApiResult
from deepdream.utils import Notifier


log = logging.getLogger()


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
            return True
        log.error(f"Error while processing job: {self.__dict__}, message: {output.message}")
        self.errors += 1
        if self.errors == self._MAX_ERRORS:
            raise TooManyErrorsException(
                f"The processing of the current job terminated because there were more than {self._MAX_ERRORS} errors."
            )
        return False

    def iterate(self) -> bool:
        """ returns true if another iteration in needed, otherwise it returns false """
        if self.iterations_left == 0:
            return False
        if self.dream():
            self.iterations_left -= 1
        return True

    def notify(self):
        """ notify user through chosen notifier """
        # TODO
        self.notifier.notify(self.user_data, {})


class DreamQueue:

    # Thread safe singleton Queue

    _instance = None

    def __init__(self):
        """ Virtually private constructor. """
        if DreamQueue._instance is not None:
            raise Exception("This class is a singleton!")
        DreamQueue._instance = self
        self.queue = []

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    @threadsafe
    def add_job(self, job: DreamJob):
        self.queue.append(job)  # TODO take job priority into account

    @threadsafe
    def take_job(self) -> DreamJob or None:
        if len(self.queue) == 0:
            return None
        job = self.queue[0]
        self.queue.pop(0)
        return job

    @staticmethod
    def get_instance():
        if DreamQueue._instance is None:
            DreamQueue._instance = DreamQueue()
        return DreamQueue._instance
