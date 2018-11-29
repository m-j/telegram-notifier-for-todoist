from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import List, Set


@dataclass(frozen=True)
class PendingNotificationEntry:
    reminder_id: int
    recipient: int
    notification_text: str
    due_date: datetime


# this should prevent puting same notifications again so they'll not be sent twice
class PendingNotificationsStore:
    _notifications: Set[PendingNotificationEntry]
    _sent: Set[PendingNotificationEntry]

    def __init__(self):
        self._notifications = set()
        self._notifications = set()
        self._notifications_lock = Lock()

    def put(self, new_entries: Set[PendingNotificationEntry]):
        with self._notifications_lock:
            self._notifications |= new_entries
            print('current notifications: ')
            print(self._notifications)

    def get(self, recipient: int):
        with self._notifications_lock:
            notifications_to_send = {n for n in self._notifications if n.recipient == recipient}
            self.sent |= notifications_to_send
            return notifications_to_send
