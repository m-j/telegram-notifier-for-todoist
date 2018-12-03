import logging
from dataclasses import dataclass
from threading import Lock
from typing import Tuple, List

from redis import Redis
from todoist import TodoistAPI


@dataclass
class Subscription:
    chat_id: int
    todoist_api: TodoistAPI


@dataclass
class SubscriptionDto:
    chat_id: int
    todoist_api_key: str


class SubscriptionsStore:
    _redis: Redis
    _subscriptions: List = []
    _lock: Lock = Lock()

    def __init__(self, redis: Redis):
        self._redis = redis

    def subscribe(self, chat_id: int, todoist_key: str):
        # TODO: check if already subscribed if yes return

        with self._lock:
            self._subscriptions.append(Subscription(chat_id, TodoistAPI(todoist_key)))
        logging.info(f'User with telegram id {chat_id} subcribed')

    def unsubscribe(self, chat_id):
        with self._lock:
            self._subscriptions = filter(lambda item: item.chat_id != chat_id, self._subscriptions)
        logging.info(f'User with telegram id {chat_id} unsubcribed')

    def get_subscriptions(self) -> Tuple[Subscription]:
        return tuple(self._subscriptions)
