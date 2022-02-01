from re import match, findall
from typing import List

from telegram import InlineKeyboardMarkup

from TelgramWrapper.bot import TelegramFunctionBlueprint, TelegramEvent


FORMATTING_REGEX = r"\{([a-zA-Z]+)\}"


# Formatting ----

def _format_message(message_text: str, variables: List[str], event: TelegramEvent) -> str:
    result_message = message_text
    for var in variables:
        result_message = result_message.replace(f"{{{var}}}", event.context.chat_data.get(var, ""))
    return result_message


def _has_formatting(message_text: str) -> bool:
    return match(FORMATTING_REGEX, message_text) is not None


def _get_variable_names(message_text: str) -> List[str]:
    result: List[str] = []
    matches = findall(FORMATTING_REGEX, message_text)
    for variable in matches:
        if variable not in result:
            result.append(variable)
    return result


# No formatting behaviours ----

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
            text of the message to send, if '{something}' is found in the text then the TelgramWrapper will try to format the
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
            self.variables = _get_variable_names(text)
            if type(keyboard) == callable:
                self.behaviour = self._format_and_call
            else:
                self.behaviour = self._format_and_send
        else:
            if type(keyboard) == callable:
                self.behaviour = _send_and_call
            else:
                self.behaviour = _send_and_send

    def _format_and_call(self, text: str, keyboard_func: callable, event: TelegramEvent):
        event.context.bot.send_message(
            text=_format_message(text, self.variables, event),
            keyboard_markup=keyboard_func(event)
        )

    def _format_and_send(self, text: str, keyboard: InlineKeyboardMarkup, event: TelegramEvent):
        event.context.bot.send_message(
            text=_format_message(text, self.variables, event),
            keyboard_markup=keyboard
        )

    def logic(self, event: TelegramEvent):
        self.behaviour(self.text, self.keyboard, event)
        return self.return_value
