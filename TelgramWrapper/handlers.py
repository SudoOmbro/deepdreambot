from telegram.ext import CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

from TelgramWrapper.generics import TelegramFunctionBlueprint


END_CONVERSATION = ConversationHandler.END


class KeyboardHandler(CallbackQueryHandler):
    pass


class TextHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.text & (~Filters.command), callback, **kwargs)


class PhotoHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.photo, callback, **kwargs)
