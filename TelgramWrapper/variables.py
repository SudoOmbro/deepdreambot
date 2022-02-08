from re import match

from TelgramWrapper.bot import TelegramFunctionBlueprint, TelegramEvent


class TelegramGetVariableGeneric(TelegramFunctionBlueprint):

    def __init__(self, var_name: str, transformation_function: callable = None, return_value: int or None = None):
        """
        Generic class to handle variables in the wrapper

        :param var_name:
            name of the variable to store, this will be put in context.chat_data
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
        self.var_name = var_name
        self.transformation_func = transformation_function
        self.return_value = return_value

    def get_from_source(self, event: TelegramEvent):
        """ virtual function to implement """
        return None

    def logic(self, event: TelegramEvent):
        """ controls the storing process & handles the calling of the transformation function """
        if self.transformation_func:
            event.context.chat_data[self.var_name] = self.transformation_func(self.get_from_source(event))
        else:
            event.context.chat_data[self.var_name] = self.get_from_source(event)
        return self.return_value


class TelegramGetText(TelegramGetVariableGeneric):

    def __init__(
            self,
            var_name: str,
            transformation_function: callable = None,
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
        raise ValueError(self.error_message)

    @staticmethod
    def get_no_validation(event: TelegramEvent):
        return event.update.message.text


class TelegramGetQuery(TelegramGetVariableGeneric):

    def get_from_source(self, event: TelegramEvent):
        return event.update.callback_query.data


class TelegramGetImage(TelegramGetVariableGeneric):

    def get_from_source(self, event: TelegramEvent):
        image_id: int = event.update.message.photo[-1].file_id
        return event.context.bot.getFile(image_id).download_as_bytearray()