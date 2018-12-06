import logging

from notifications_watch.notifications_watcher import NotificationsWatcher
from notifications_watch.pending_notifications_store import PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore, load_subscriptions_store
from telegram_bot.notifier_bot import NotifierBot
from utils.create_redis_client import create_redis_client
from utils.load_api_keys import load_config
import redis

config = load_config()
todist_api_key = config['todoist_api_key']
telegram_token = config['telegram_bot_token']
redis_connection_string = config['redis']
subscriber_password = config['subscriber_password']

logging.basicConfig(level=logging.INFO)


def main():
    redis_client = create_redis_client(redis_connection_string)

    pending_notifications_store = PendingNotificationsStore()

    subscriptions_store = load_subscriptions_store(redis=redis_client)

    notifications_watcher = NotificationsWatcher(pending_notifications_store, subscriptions_store)
    notifications_watcher.start()

    notifier_bot = NotifierBot(telegram_token, subscriptions_store, pending_notifications_store, subscriber_password)
    notifier_bot.start()


main()