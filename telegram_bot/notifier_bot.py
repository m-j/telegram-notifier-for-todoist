import logging
from typing import List

from telegram import Update, Bot, User
from telegram.ext import Updater, CommandHandler

from subscriptions.subscriptions_store import SubscriptionsStore, Subcription


def help_command(bot, update):
    update.message.reply_text('Help!')

class NotifierBot:
    _updater: Updater
    _subscriptions_store: SubscriptionsStore

    def __init__(self, telegram_token: str, subriptions_store: SubscriptionsStore):
        self._updater = Updater(token=telegram_token)
        self._subscriptions_store = SubscriptionsStore()

    def help_command(self, bot, update):
        update.message.reply_text('Help!')

    def sub_command(self, bot: Bot, update: Update, args: List[str]):
        user: User = update.effective_user

        if len(args) == 1:
            logging.info(f'Received /sub message from user {user.full_name} with user id {user.id}')
            self._subscriptions_store.subscribe(telegram_id=user.id, todoist_key=args[0])
            update.message.reply_text(f'{user.full_name}, you\'ve been subscribed for notifications')
        else:
            update.message.reply_text('usage:\n/sub [todoist_api_key]')

    def start(self):
        dp = self._updater.dispatcher

        dp.add_handler(CommandHandler('help', self.help_command))
        dp.add_handler(CommandHandler('sub', self.sub_command, pass_args=True))

        self._updater.start_polling()
        self._updater.idle()