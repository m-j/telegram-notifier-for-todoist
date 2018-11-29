from telegram.ext import Updater, CommandHandler


def help_command(bot, update):
    update.message.reply_text('Help!')

class NotifierBot:
    _updater: Updater

    def __init__(self, telegram_token: str):
        self._updater = Updater(token=telegram_token)

    def help_command(self, bot, update):
        update.message.reply_text('Help!')

    def start(self):
        dp = self._updater.dispatcher

        dp.add_handler(CommandHandler('help', self.help_command))

        self._updater.start_polling()
        self._updater.idle()