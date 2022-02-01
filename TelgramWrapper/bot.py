import logging

from telegram import Update
from telegram.ext import Updater, CallbackContext, Dispatcher, Handler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TelegramEvent:

    def __init__(self, update: Update, context: CallbackContext):
        self.update: Update = update
        self.context: CallbackContext = context
        self.chat_id: int = update.effective_chat.id  # for convenience


class TelegramFunctionBlueprint:

    def __call__(self, update: Update, context: CallbackContext):
        return self.logic(TelegramEvent(update, context))

    def logic(self, event: TelegramEvent):
        pass


class TelegramBot:

    def __init__(self, token: str):
        self.updater: Updater = Updater(token=token, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher

    def add_handler(self, handler: Handler):
        self.dispatcher.add_handler(handler)

    def run(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()
