from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import List


@dataclass
class PendingNotificationEntry:
    reminder_id: int
    recipient: str
    notification_text: str
    due_date: datetime


# this should prevent puting same notifications again so they'll not be sent twice
class PendingNotificationsStore:
    _notifications: List[PendingNotificationEntry]

    def __init__(self):
        self._notifications = []
        self._notifications_lock = Lock()

    def put(self, entries: List[PendingNotificationEntry]):
        with self._notifications_lock:
            self._notifications.extend(entries)

    def get(self):
        pass