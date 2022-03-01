from typing import Dict, Tuple

from TelgramWrapper.generics import TelegramEvent

[

    CONTEXT_VARIABLE,
    CONTEXT_DICT,
    CONTEXT_OBJECT,
    UPDATE

] = range(4)


class MATEVarHandler:

    HANDLERS: Dict[int, Tuple[callable, callable or None]]

    # handlers structure:
    # type - handler, lambda to get the args or None

    def __init__(self, target):
        var_type = self.__get_access_type(target)
        handlers: Tuple[callable, callable] = self.HANDLERS.get(var_type, None)
        if not handlers:
            raise ValueError(f"No handler for var_type {var_type} (target: {target})")
        self.logic: callable = handlers[0]
        if handlers[1]:
            self.args = handlers[1](target)

    @staticmethod
    def __get_access_type(target: str):
        if target.find(":"):
            return CONTEXT_DICT
        elif target.find("."):
            return CONTEXT_OBJECT
        elif target[:2] == "__":
            return UPDATE
        else:
            return CONTEXT_VARIABLE


class MATEVarGetter(MATEVarHandler):

    def __get_variable(self, event: TelegramEvent):
        return event.context.chat_data[self.args]

    def __get_dict(self, event: TelegramEvent):
        return event.context.chat_data[self.args[0]][self.args[1]]

    def __get_object(self, event: TelegramEvent):
        return event.context.chat_data[self.args[0]].__dict__[self.args[1]]

    def __get_from_update(self, event: TelegramEvent):
        return event.update.effective_user[self.args]

    HANDLERS = {
        CONTEXT_VARIABLE: (
            __get_variable,
            None
        ),
        CONTEXT_DICT: (
            __get_dict,
            lambda target: target.split(":")
        ),
        CONTEXT_OBJECT: (
            __get_dict,
            lambda target: target.split(".")
        ),
        UPDATE: (
            __get_from_update,
            lambda target: target[2:]
        )
    }


class MATEVarSetter(MATEVarHandler):

    def __set_variable(self, user_input, event: TelegramEvent):
        event.context.chat_data[self.args] = user_input

    def __set_object(self, user_input, event: TelegramEvent):
        event.context.chat_data[self.args[0]].__dict__[self.args[1]] = user_input

    def __set_dict(self, user_input, event: TelegramEvent):
        if event.context.chat_data[self.args[0]] is None:
            event.context.chat_data[self.args[0]] = {}
        event.context.chat_data[self.args[0]][self.args[1]] = user_input

    HANDLERS = {
        CONTEXT_VARIABLE: (
            __set_variable,
            None
        ),
        CONTEXT_DICT: (
            __set_dict,
            lambda target: target.split(":")
        ),
        CONTEXT_OBJECT: (
            __set_object,
            lambda target: target.split(".")
        )
    }
