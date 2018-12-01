from dataclasses import dataclass
from threading import Lock
from typing import Tuple, List
import logging


@dataclass
class Subcription:
    telegram_id: int
    todoist_key: str


class SubscriptionsStore:
    _subscriptions: List = []
    _lock: Lock = Lock()

    def subscribe(self, telegram_id: int, todoist_key: str):
        with self._lock:
            self._subscriptions.append(Subcription(telegram_id, todoist_key))
        logging.info(f'User with telegram id {telegram_id} subcribed')

    def unsubscribe(self, telegram_id):
        with self._lock:
            self._subscriptions = filter(lambda item: item.telegram_id != telegram_id, self._subscriptions)
        logging.info(f'User with telegram id {telegram_id} unsubcribed')

    def get_subs(self) -> Tuple[Subcription]:
        return tuple(self._subscriptions)
