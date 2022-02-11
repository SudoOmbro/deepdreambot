from telegram import InlineKeyboardMarkup, InlineKeyboardButton


MAIN_KEYBOARD = InlineKeyboardMarkup([

    [InlineKeyboardButton("Dream", callback_data="back")],
    [InlineKeyboardButton("Buy me a coffee", callback_data="norm")]
])
