from threading import Thread
from time import sleep

import todoist
from datetime import datetime, timezone, timedelta

from notifications_watch.pending_notifications_store import PendingNotificationEntry, PendingNotificationsStore

date_time_format = '%a %d %b %Y %H:%M:%S %z'
reminder_time_window = timedelta(minutes=60)


class NotificationsWatcher:
    api: todoist.TodoistAPI
    enabled: bool
    thread: Thread
    pending_notifications_store: PendingNotificationsStore

    def __init__(self, todoist_api_key:str, pending_notifications_store : PendingNotificationsStore):
        self.api = todoist.TodoistAPI(todoist_api_key)
        self.enabled = False
        self.thread = Thread(target=self.run)
        self.pending_notifications_store = pending_notifications_store

    def run(self):
        self.enabled = True

        while self.enabled:
            sync_response = self.api.sync()
            if 'http_code' in sync_response and sync_response['http_code'] > 300:
                raise Exception('Failed to sync ' + str(sync_response))

            reminders = self.api.reminders.all()

            aware_now = datetime.now(timezone.utc)

            # api does not contain reminders from past
            # we'll have to look for reminders that will be in past within some interval (like 10 minutes

            passed_reminders = [
                reminder for reminder in reminders if
                aware_now + reminder_time_window >= datetime.strptime(reminder.data['due_date_utc'], date_time_format)
            ]

            user_id = self.api.user.get_id()

            print(f'user_id {user_id}')

            notification_entries = [
                PendingNotificationEntry(
                    reminder_id=reminder.data['id'],
                    recipient=reminder.data['notify_uid'],
                    due_date=reminder.data['due_date_utc'],
                    notification_text=self.api.items.get_by_id(reminder.data['item_id']).data['content']
                                         )
                for reminder in passed_reminders
            ]

            self.pending_notifications_store.put(set(notification_entries))

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