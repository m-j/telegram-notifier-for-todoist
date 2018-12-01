import logging
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from time import sleep
from typing import List

import todoist
from datetime import datetime, timezone, timedelta

from notifications_watch.pending_notifications_store import PendingNotificationEntry, PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore, Subscription

date_time_format = '%a %d %b %Y %H:%M:%S %z'
reminder_time_window = timedelta(minutes=10)


class NotificationsWatcher:
    _subscriptions_store: SubscriptionsStore
    api: todoist.TodoistAPI
    enabled: bool
    thread: Thread
    _pending_notifications_store: PendingNotificationsStore

    def __init__(self, pending_notifications_store: PendingNotificationsStore, subscriptions_store: SubscriptionsStore):
        self._subscriptions_store = subscriptions_store
        self._pending_notifications_store = pending_notifications_store

        self.enabled = False
        self.thread = Thread(target=self.run)

    def _sync(self, subscription: Subscription) -> List[PendingNotificationEntry]:
        api = subscription.todoist_api

        sync_response = api.sync()
        if 'http_code' in sync_response and sync_response['http_code'] > 300:
            raise Exception('Failed to sync ' + str(sync_response))

        reminders = api.reminders.all()

        aware_now = datetime.now(timezone.utc)

        passed_reminders = [
            reminder for reminder in reminders if
            aware_now + reminder_time_window >= datetime.strptime(reminder.data['due_date_utc'], date_time_format)
        ]

        user_id = api.user.get_id()

        print(f'user_id {user_id}')

        notification_entries = [
            PendingNotificationEntry(
                reminder_id=reminder.data['id'],
                due_date=reminder.data['due_date_utc'],
                text=api.items.get_by_id(reminder.data['item_id']).data['content'],
                chat_id=subscription.chat_id
            )
            for reminder in passed_reminders
        ]

        return notification_entries

    def run(self):
        self.enabled = True

        while self.enabled:
            subs = self._subscriptions_store.get_subscriptions()
            with ThreadPoolExecutor() as executor:
                notification_entry_futures = [executor.submit(self._sync, sub) for sub in subs]
                for f in futures.as_completed(notification_entry_futures):
                    try:
                        entries = f.result()
                        self._pending_notifications_store.put(set(entries))
                    except Exception as ex:
                        logging.error(f'Failed to sync')
                        logging.error(ex)

            sleep(5)

    def start(self):
        self.enabled = True
        self.thread.start()

    def stop(self):
        self.enabled = False
        self.thread.join(5)