import logging
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread
from time import sleep
from typing import List, Dict

import todoist
from datetime import datetime, timezone, timedelta

from notifications_watch.pending_notifications_store import PendingNotificationEntry, PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore, Subscription

date_time_format = '%a %d %b %Y %H:%M:%S %z'
time_window_forward = timedelta(minutes=10)  # look that much in the future
time_window_backward = timedelta(minutes=10)  # look that much in the past


def is_within_time_window(now, d: datetime):
    return now + time_window_forward >= d >= now - time_window_backward


def item_predicate(item: Dict) -> bool:
    return item.data['due_date_utc'] is not None and item['priority'] > 1 and not item['checked']


def notifications_from_reminders(api: todoist.TodoistAPI, aware_now, chat_id):
    reminders = api.reminders.all()

    passed_reminders = [
        reminder for reminder in reminders if
        (reminder.data['due_date_utc'] is not None) and
        (aware_now + time_window_forward >= datetime.strptime(reminder.data['due_date_utc'], date_time_format))
    ]
    user_id = api.user.get_id()
    print(f'user_id {user_id}')

    notification_entries = [
        PendingNotificationEntry(
            reminder_id=reminder.data['id'],
            due_date=reminder.data['due_date_utc'],
            text=api.items.get_by_id(reminder.data['item_id']).data['content'],
            chat_id=chat_id
        )
        for reminder in passed_reminders
    ]
    return notification_entries


def notifications_from_items(api: todoist.TodoistAPI, aware_now, chat_id):
    items = api.items.all()

    passed_items = [
        item for item in items if
        item_predicate(item) and
        is_within_time_window(aware_now, datetime.strptime(item.data['due_date_utc'], date_time_format))
    ]

    user_id = api.user.get_id()
    print(f'user_id {user_id}')

    notification_entries = [
        PendingNotificationEntry(
            reminder_id=item.data['id'],
            due_date=item.data['due_date_utc'],
            text=item.data['content'],
            chat_id=chat_id
        )
        for item in passed_items
    ]
    return notification_entries


def _sync(subscription: Subscription) -> List[PendingNotificationEntry]:
    api = subscription.todoist_api

    sync_response = api.sync()
    if 'http_code' in sync_response and sync_response['http_code'] > 300:
        raise Exception('Failed to sync ' + str(sync_response))

    aware_now = datetime.now(timezone.utc)

    notification_entries = notifications_from_items(api, aware_now, subscription.chat_id)

    return notification_entries


class NotificationsWatcher:
    _subscriptions_store: SubscriptionsStore
    enabled: bool
    thread: Thread
    _pending_notifications_store: PendingNotificationsStore

    def __init__(self, pending_notifications_store: PendingNotificationsStore, subscriptions_store: SubscriptionsStore):
        self._subscriptions_store = subscriptions_store
        self._pending_notifications_store = pending_notifications_store

        self.enabled = False
        self.thread = Thread(target=self.run)

    def run(self):
        self.enabled = True

        while self.enabled:
            subs = self._subscriptions_store.get_subscriptions()
            with ThreadPoolExecutor() as executor:
                notification_entry_futures = [executor.submit(_sync, sub) for sub in subs]
                for f in futures.as_completed(notification_entry_futures):
                    try:
                        entries = f.result()
                        self._pending_notifications_store.put(set(entries))
                    except Exception as ex:
                        logging.exception(f'Failed to sync')
                        # logging.error(ex)

            sleep(5)

    def start(self):
        self.enabled = True
        self.thread.start()

    def stop(self):
        self.enabled = False
        self.thread.join(5)
