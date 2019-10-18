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

# date_time_format = '%a %d %b %Y %H:%M:%S'
date_time_format = '%Y-%m-%dT%H:%M:%S'
time_window_forward = timedelta(minutes=10)  # look that much in the future
time_window_backward = timedelta(minutes=10)  # look that much in the past


def is_within_time_window(now, d: datetime):
    return now + time_window_forward >= d >= now - time_window_backward


def item_predicate(item: Dict) -> bool:
    return 'due' in item.data and item.data['priority'] > 1 and not item.data['checked']


def is_item_within_time_window(item, aware_now):
    if 'T' in item['due']['date']:
        date_str = item.data['due']['date'].replace('Z', '')
        return is_within_time_window(aware_now, datetime.strptime(date_str, date_time_format))
    else:
        False


def notifications_from_items(api: todoist.TodoistAPI, aware_now, chat_id):
    items = api.items.all()

    due_items = [
        item for item in items if
        item_predicate(item)
    ]

    passed_items = [
        item for item in due_items if is_item_within_time_window(item, aware_now)
    ]

    user_id = api.user.get_id()
    print(f'user_id {user_id}')

    notification_entries = [
        PendingNotificationEntry(
            reminder_id=item.data['id'],
            due_date=item.data['due']['date'],
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

    aware_now = datetime.now()

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
