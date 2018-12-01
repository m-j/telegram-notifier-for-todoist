from typing import List

from telegram import Update, Bot, User
from telegram.ext import Updater, CommandHandler


def help_command(bot, update):
    update.message.reply_text('Help!')

class NotifierBot:
    _updater: Updater

    def __init__(self, telegram_token: str):
        self._updater = Updater(token=telegram_token)

    def help_command(self, bot, update):
        update.message.reply_text('Help!')

    def sub_command(self, bot : Bot, update : Update, args: List[str]):
        if len(args) == 1:
            print('subscribe!')
            user: User = update.effective_user
            update.message.reply_text(f'Hello {user.full_name}')
        else:
            update.message.reply_text('usage:\n/sub [todoist_api_key]')

    def start(self):
        dp = self._updater.dispatcher

        dp.add_handler(CommandHandler('help', self.help_command))
        dp.add_handler(CommandHandler('sub', self.sub_command, pass_args=True))

        self._updater.start_polling()
        self._updater.idle()