from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import List, Set


@dataclass(frozen=True)
class PendingNotificationEntry:
    reminder_id: int
    chat_id: int
    text: str
    due_date: datetime


class PendingNotificationsStore:
    _notifications: Set[PendingNotificationEntry]
    _sent: Set[PendingNotificationEntry]

    def __init__(self):
        self._notifications = set()
        self._sent = set()
        self._notifications_lock = Lock()

    def put(self, new_entries: Set[PendingNotificationEntry]):
        with self._notifications_lock:
            self._notifications |= new_entries
            print('current notifications: ')
            print(self._notifications)

    def get(self) -> Set[PendingNotificationEntry]:
        with self._notifications_lock:
            notifications_to_send = {n for n in self._notifications if n not in self._sent}
            self._sent |= notifications_to_send
            return notifications_to_send
