import logging

from notifications_watch.notification_sync_scheduler import NotificationSyncScheduler
from notifications_watch.notifications_watcher import NotificationsWatcher
from notifications_watch.pending_notifications_store import PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore
from telegram_bot.notifier_bot import NotifierBot
from utils.load_api_keys import load_api_keys

api_keys = load_api_keys()
todist_api_key = api_keys['todoist_api_key']
telegram_token = api_keys['telegram_bot_token']

logging.basicConfig(level=logging.INFO)

def main():
    pending_notifications_store = PendingNotificationsStore()

    subscriptions_store = SubscriptionsStore()
    # notifications_watcher = NotificationsWatcher(todoist_api_key=todist_api_key,
    #                                              pending_notifications_store=pending_notifications_store)
    # notifications_watcher.start()

    notification_sync_scheduler = NotificationSyncScheduler()


    notifier_bot = NotifierBot(telegram_token, subscriptions_store, pending_notifications_store)
    notifier_bot.start()


main()