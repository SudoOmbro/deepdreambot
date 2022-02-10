import logging

from telegram.ext import Updater, CallbackContext, Dispatcher, Handler

from TelgramWrapper.generics import TelegramUserError

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def default_error_handler(update, context: CallbackContext):
    error: Exception = context.error
    if type(error) == TelegramUserError:
        context.bot.send_message(error)
    else:
        logger.error(f"Error: {error}\n\ndue to update: {update.to_dict()}")


class TelegramBot:

    def __init__(self, token: str, error_handler: callable = None):
        self.updater: Updater = Updater(token=token, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        if error_handler:
            self.dispatcher.add_error_handler(error_handler)
        else:
            self.dispatcher.add_error_handler(default_error_handler)

    def add_handler(self, handler: Handler):
        self.dispatcher.add_handler(handler)

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def start_and_idle(self):
        self.updater.start_polling()
        self.updater.idle()
        self.updater.stop()
