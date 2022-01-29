import re

from telegram import InlineKeyboardMarkup

from bot.bot import TelegramFunctionBlueprint, TelegramEvent


FORMATTING_REGEX = r"\{.+\}"


def _format_message(message_text: str, event: TelegramEvent) -> str:
    # TODO
    return message_text


def _has_formatting(message_text: str) -> bool:
    return re.match(FORMATTING_REGEX, message_text) is not None


# Behaviours

def _format_and_call(text: str, keyboard_func: callable, event: TelegramEvent):
    event.context.bot.send_message(
        text=_format_message(text, event),
        keyboard_markup=keyboard_func(event)
    )


def _format_and_send(text: str, keyboard: InlineKeyboardMarkup, event: TelegramEvent):
    event.context.bot.send_message(
        text=_format_message(text, event),
        keyboard_markup=keyboard
    )


def _send_and_call(text: str, keyboard_func: callable, event: TelegramEvent):
    event.context.bot.send_message(
        text=text,
        keyboard_markup=keyboard_func(event)
    )


def _send_and_send(text: str, keyboard: InlineKeyboardMarkup, event: TelegramEvent):
    event.context.bot.send_message(
        text=text,
        keyboard_markup=keyboard
    )


class TelegramSendPrompt(TelegramFunctionBlueprint):

    def __init__(self, text: str, keyboard: InlineKeyboardMarkup or callable = None, return_value: int or None = None):
        """
        Class to handle sending prompts via Telegram.

        :param text:
            text of the message to send, if '{something}' is found in the text then the bot will try to format the
            text replacing all '{something}' instances with whatever context.chat_data['something'] contains.
        :param keyboard:
            the inline keyboard to send or the function that will generate the inline keyboard to send.
            Leave as None to not send any keyboard.
        :param return_value:
            the return value of the function, used to change state in conversation handlers.
            Leave at None to not change state.
        """
        self.text = text
        self.keyboard = keyboard
        self.return_value = return_value
        if _has_formatting(text):
            if type(keyboard) == callable:
                self.behaviour = _format_and_call
            else:
                self.behaviour = _format_and_send
        else:
            if type(keyboard) == callable:
                self.behaviour = _send_and_call
            else:
                self.behaviour = _send_and_send

    def logic(self, event: TelegramEvent):
        self.behaviour(self.text, self.keyboard, event)
        return self.return_value
