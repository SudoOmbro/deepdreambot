from telegram import InlineKeyboardMarkup, InlineKeyboardButton


MAIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("Dream", callback_data="dream")],
    [InlineKeyboardButton("About", callback_data="about")],
    [InlineKeyboardButton("Buy me a coffee", url="https://www.paypal.com/donate?hosted_button_id=UBNSEND5E96H2")]
])
