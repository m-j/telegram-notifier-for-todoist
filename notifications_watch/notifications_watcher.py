from threading import Thread
from time import sleep

import todoist
from datetime import datetime, timezone, timedelta

from notifications_watch.pending_notifications_store import PendingNotificationEntry, PendingNotificationsStore
from subscriptions.subscriptions_store import SubscriptionsStore, Subscription

date_time_format = '%a %d %b %Y %H:%M:%S %z'
reminder_time_window = timedelta(minutes=60)


class NotificationsWatcher:
    _subscriptions_store: SubscriptionsStore
    api: todoist.TodoistAPI
    enabled: bool
    thread: Thread
    _pending_notifications_store: PendingNotificationsStore

    def __init__(self, pending_notifications_store: PendingNotificationsStore, subscriptions_store: SubscriptionsStore):
        self._subscriptions_store = subscriptions_store
        self._pending_notifications_store = pending_notifications_store

        # self.api = todoist.TodoistAPI(todoist_api_key)
        self.enabled = False
        self.thread = Thread(target=self.run)

    def _sync(self, subscription: Subscription):
        api = subscription.todoist_api

        sync_response = api.sync()
        if 'http_code' in sync_response and sync_response['http_code'] > 300:
            raise Exception('Failed to sync ' + str(sync_response))

        reminders = api.reminders.all()

        aware_now = datetime.now(timezone.utc)

        # api does not contain reminders from past
        # we'll have to look for reminders that will be in past within some interval (like 10 minutes

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

        self._pending_notifications_store.put(set(notification_entries))

    def run(self):
        self.enabled = True

        while self.enabled:
            subs = self._subscriptions_store.get_subscriptions()
            for sub in subs:
                self._sync(sub)

            sleep(5)

    def start(self):
        self.enabled = True
        self.thread.start()

    def stop(self):
        self.enabled = False
        self.thread.join(5)


# Loop:
#   Read registered subs = (todoist, telgram)
#   Foreach sub:
#       create future that will run sync and retrieve list of notofications
#
# !!! Keep in mind that sync is incremental and therefore you want to keep all todoist api object alive between syncs
# ??? Maybe queue producer/consumre then?