from bot.bot import TelegramFunctionBlueprint, TelegramEvent, TelegramBot


class TelegramNotifier:
    pass


class TelegramGetImage(TelegramFunctionBlueprint):

    def __init__(self, get_from_url: bool):
        if get_from_url:
            self.func: callable = self.get_image_from_url
        else:
            self.func: callable = self.get_image_from_image

    def get_image_from_image(self, event: TelegramEvent) -> int:
        # TODO
        return 0

    def get_image_from_url(self, event: TelegramEvent) -> int:
        # TODO
        return 0

    def logic(self, event: TelegramEvent):
        queue_position = self.func(event)
        event.context.bot.send_message(
            chat_id=event.chat_id,
            text=f"you have been placed in queue at position {queue_position}"
        )


if __name__ == "__main__":
    pass
