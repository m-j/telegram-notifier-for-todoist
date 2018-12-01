from dataclasses import dataclass
from threading import Lock
from typing import Tuple, List
import logging
import todoist
from todoist import TodoistAPI


@dataclass
class Subscription:
    chat_id: int
    todoist_api: TodoistAPI


class SubscriptionsStore:
    _subscriptions: List = []
    _lock: Lock = Lock()

    def subscribe(self, chat_id: int, todoist_key: str):
        with self._lock:
            self._subscriptions.append(Subscription(chat_id, TodoistAPI(todoist_key)))
        logging.info(f'User with telegram id {chat_id} subcribed')

    def unsubscribe(self, chat_id):
        with self._lock:
            self._subscriptions = filter(lambda item: item.chat_id != chat_id, self._subscriptions)
        logging.info(f'User with telegram id {chat_id} unsubcribed')

    def get_subscriptions(self) -> Tuple[Subscription]:
        return tuple(self._subscriptions)
