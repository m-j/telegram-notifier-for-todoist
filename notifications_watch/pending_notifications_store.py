from dataclasses import dataclass
from datetime import datetime
from threading import Lock


@dataclass
class PendingNotificationEntry:
    recipient: str
    notification_text: str
    due_date: datetime


class PendingNotificationsStore:
    _notifications: list[PendingNotificationEntry]

    def __init__(self):
        self._notifications = []
        self._notifications_lock = Lock()

    def put(self, entries: list[PendingNotificationEntry]):
        with self._notifications_lock:
            self._notifications.extend(entries)

    def get(self):
        pass