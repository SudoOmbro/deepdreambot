from copy import deepcopy
from re import match

from telegram import Update
from telegram.ext import CallbackContext

from TelgramWrapper.generics import TelegramFunctionBlueprint, TelegramEvent, TelegramUserError


class TelegramGetVariableGeneric(TelegramFunctionBlueprint):

    def __init__(self, var_name: str or None, transformation_function: callable = None, return_value: int or None = None):
        """
        Generic class to handle variables in the wrapper

        :param var_name:
            name of the variable to store, this will be put in context.chat_data

            if you pass None (and return value is None), this handler will just return the retrieved value. Useful in
            combination with transformation functions to use the gathered data in some way and then throw it away or
            to create main menus that lead to submenus.

            if you pass something like "dict_name:aaa" then this handler will try to put the received value in
            dict_name["aaa"], where dict_name is the context key for the dict and aaa is a parameter of said dict

            if you pass something like "obj_name.var" then this handler will try to put the received value in
            obj_name.var, where onj_name is the context key for the object and var is a variable of said object
        :param transformation_function:
            a function that will take the variable
            and transform it somehow before storing it.

            the function should have 1 input and 1 output, like this:

            func(input):
                return something
        :param return_value:
            the return value of the function, used to change state in conversation handlers.
            Leave at None to not change state.
        """
        # set transformation
        if transformation_function:
            self.transformation_func = transformation_function
            self.__get: callable = self.__get_from_source_transform
        else:
            self.__get: callable = self.__get_from_source_no_transform
        # set where to put the value
        if var_name:
            if var_name.find(":") != -1:
                self.logic: callable = self.__set_dict
                split_var_name = var_name.split(":")
                self.dict_name = split_var_name[0]
                self.var_name = split_var_name[1]
            elif var_name.find(".") != -1:
                self.logic: callable = self.__set_object
                split_var_name = var_name.split(".")
                self.obj_name = split_var_name[0]
                self.var_name = split_var_name[1]
            else:
                self.logic: callable = self.__set_variable
                self.var_name = var_name
        else:
            self.logic = self.__no_set
        self.return_value = return_value

    # get handling

    def __get_from_source_transform(self, event: TelegramEvent):
        return self.transformation_func(self.get_from_source(event))

    def __get_from_source_no_transform(self, event: TelegramEvent):
        return self.get_from_source(event)

    # set handling

    def __set_variable(self, event: TelegramEvent):
        event.context.chat_data[self.var_name] = self.__get(event)
        return self.return_value

    def __set_object(self, event: TelegramEvent):
        event.context.chat_data[self.obj_name].__dict__[self.var_name] = self.__get(event)
        return self.return_value

    def __set_dict(self, event: TelegramEvent):
        if event.context.chat_data[self.dict_name] is None:
            event.context.chat_data[self.dict_name] = {}
        event.context.chat_data[self.dict_name][self.var_name] = self.__get(event)
        return self.return_value

    def __no_set(self, event: TelegramEvent):
        if self.return_value:
            self.__get(event)
            return self.return_value
        return self.__get(event)

    # Abstract function that needs to be implemented

    def get_from_source(self, event: TelegramEvent):
        """ virtual function to implement """
        return None


class TelegramGetText(TelegramGetVariableGeneric):

    def __init__(
            self,
            var_name: str or None,
            transformation_function: callable or None = None,
            validation_regex: str = None,
            error_message: str = None,
            return_value: int or None = None
    ):
        """
        gets a text input from the user and optionally validates it.

        :param var_name:
            see <TelegramGetVariableGeneric>
        :param transformation_function:
            see <TelegramGetVariableGeneric>
        :param validation_regex:
            The regular expression used to validate the text input.
            Leave empty if you don't want to validate
        :param error_message:
            The error message to send the user in case the given input wasn't validated correctly.
            Leave empty for a default, generic response
        :param return_value:
            see <TelegramGetVariableGeneric>
        """
        super().__init__(var_name, transformation_function=transformation_function, return_value=return_value)
        if validation_regex:
            self.validation_regex = validation_regex
            self.get_from_source: callable = self.get_validation
        else:
            self.get_from_source: callable = self.get_no_validation
        self.error_message = error_message if error_message else "The given text doesn't match the pattern"

    def get_validation(self, event: TelegramEvent):
        text = event.update.message.text
        if match(self.validation_regex, text):
            return event.update.message.text
        raise TelegramUserError(self.error_message)

    @staticmethod
    def get_no_validation(event: TelegramEvent):
        return event.update.message.text


class TelegramGetQuery(TelegramGetVariableGeneric):

    # TODO add support for arbitrary_callback_data

    def get_from_source(self, event: TelegramEvent):
        return event.update.callback_query.data


class TelegramGetPhoto(TelegramGetVariableGeneric):

    def get_from_source(self, event: TelegramEvent):
        file = event.update.message.photo[-1].get_file()
        return bytes(file.download_as_bytearray())


def clear_vars(update: Update, context: CallbackContext):
    """ Used to clear the current user context """
    context.chat_data.clear()


class TelegramInitContext(TelegramFunctionBlueprint):

    def __init__(self, default_context: dict, clear_context: bool = False):
        """
        Used to set the given dictionary as the current user's context.

        :param default_context: the desired context
        :param clear_context: defines whether the user's context should be cleared before initializing the new one
        """
        self.default_context = default_context
        self.clear_context = clear_context

    def logic(self, event: TelegramEvent):
        if self.clear_context:
            clear_vars(event.update, event.context)
        for item in self.default_context:
            event.context.chat_data[item] = deepcopy(self.default_context[item])
