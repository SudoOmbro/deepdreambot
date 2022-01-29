import io

from PIL.Image import Image

from bot.bot import TelegramFunctionBlueprint, TelegramEvent, TelegramBot
from deepdream.jobs_queue import DreamQueue, DreamJob
from deepdream.utils import Notifier
from requests import get

from utils.url_utils import download_image


class TelegramNotifier(Notifier):
    pass


IMAGE_URL_REGEX = r"http[s]??://.*\.(?:jpg|png)"


if __name__ == "__main__":
    pass
