import logging
from typing import List

from telegram import Update, Bot, User, Chat
from telegram.ext import Updater, CommandHandler, Job

from notifications_watch.pending_notifications_store import PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore, Subscription


class NotifierBot:
    _pending_notifications_store: PendingNotificationsStore
    _updater: Updater
    _subscriptions_store: SubscriptionsStore

    def __init__(self, telegram_token: str,
                 subriptions_store: SubscriptionsStore,
                 pending_notifications_store: PendingNotificationsStore):
        self._updater = Updater(token=telegram_token)
        self._subscriptions_store = SubscriptionsStore()
        self._pending_notifications_store = pending_notifications_store

    def help_command(self, bot, update):
        update.message.reply_text('Help!')

    def sub_command(self, bot: Bot, update: Update, args: List[str]):
        user: User = update.effective_user
        chat: Chat = update.effective_chat

        if len(args) == 1:
            logging.info(f'Received /sub message from user {user.full_name} with chat id {chat.id}')
            self._subscriptions_store.subscribe(chat_id=chat.id, todoist_key=args[0])
            update.message.reply_text(f'{user.full_name}, you\'ve been subscribed for notifications')
        else:
            update.message.reply_text('usage:\n/sub [todoist_api_key]')

    def send_notifications_job(self, bot: Bot, job: Job):
        notifications_to_send = self._pending_notifications_store.get()

        for notification in notifications_to_send:
            logging.info(f'Sending notification to chat id {notification.chat_id}')
            bot.send_message(
                chat_id=notification.chat_id,
                text=notification.text
            )


    def start(self):
        dp = self._updater.dispatcher

        dp.add_handler(CommandHandler('help', self.help_command))
        dp.add_handler(CommandHandler('sub', self.sub_command, pass_args=True))

        dp.job_queue.run_repeating(self.send_notifications_job, interval=10, first=10)

        self._updater.start_polling()
        self._updater.idle()