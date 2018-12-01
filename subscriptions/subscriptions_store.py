from dataclasses import dataclass
from threading import Lock
from typing import Tuple, List
import logging


@dataclass
class Subcription:
    chat_id: int
    todoist_key: str


class SubscriptionsStore:
    _subscriptions: List = []
    _lock: Lock = Lock()

    def subscribe(self, chat_id: int, todoist_key: str):
        with self._lock:
            self._subscriptions.append(Subcription(chat_id, todoist_key))
        logging.info(f'User with telegram id {chat_id} subcribed')

    def unsubscribe(self, chat_id):
        with self._lock:
            self._subscriptions = filter(lambda item: item.chat_id != chat_id, self._subscriptions)
        logging.info(f'User with telegram id {chat_id} unsubcribed')

    def get_subs(self) -> Tuple[Subcription]:
        return tuple(self._subscriptions)
