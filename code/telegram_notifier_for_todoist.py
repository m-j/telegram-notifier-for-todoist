import logging

from notifications_watch.notifications_watcher import NotificationsWatcher
from notifications_watch.pending_notifications_store import PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore
from telegram_bot.notifier_bot import NotifierBot
from utils.create_redis_client import create_redis_client
from utils.load_api_keys import load_config
import redis

config = load_config()
todist_api_key = config['todoist_api_key']
telegram_token = config['telegram_bot_token']
redis_connection_string = config["redis"]

logging.basicConfig(level=logging.INFO)

def main():
    pending_notifications_store = PendingNotificationsStore()

    subscriptions_store = SubscriptionsStore()

    notifications_watcher = NotificationsWatcher(pending_notifications_store, subscriptions_store)
    notifications_watcher.start()

    notifier_bot = NotifierBot(telegram_token, subscriptions_store, pending_notifications_store)
    notifier_bot.start()


# main()

redis_client = create_redis_client(redis_connection_string)
redis_client.lpush('test', 'xxx')
redis_client.lpush('test', 'yyy')