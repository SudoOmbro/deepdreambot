from telegram.ext import CallbackQueryHandler, MessageHandler, Filters

from TelgramWrapper.generics import TelegramFunctionBlueprint


class KeyboardHandler(CallbackQueryHandler):
    pass


class TextHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.text & (~Filters.command), callback, **kwargs)


class PhotoHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.photo, callback, **kwargs)
