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

    def get_from_source(self, event: TelegramEvent):
        return event.update.message.text


class TelegramGetImage(TelegramGetVariableGeneric):

    def get_from_source(self, event: TelegramEvent):
        image_id: int = event.update.message.photo[-1].file_id
        return event.context.bot.getFile(image_id).download_as_bytearray()