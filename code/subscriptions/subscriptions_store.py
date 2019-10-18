import logging
from dataclasses import dataclass
from json import dumps, loads, JSONDecodeError
from threading import Lock
from typing import Tuple, List

from redis import Redis
from todoist import TodoistAPI

from utils import redis_keys


@dataclass
class Subscription:
    chat_id: int
    todoist_api: TodoistAPI


def load_subscriptions_store(redis: Redis):
    try:
        subscription_jsons = redis.lrange(redis_keys.subscription, 0, -1)

        subscription_dicts = [loads(sjs) for sjs in subscription_jsons]

        subscriptions = [
            Subscription(
                chat_id=sdict['chat_id'],
                todoist_api=TodoistAPI(token=sdict['todoist_key'], cache=None, api_endpoint='https://api.todoist.com'))
            for sdict in subscription_dicts
        ]

        logging.info('Successfully loaded notifications from redis.')
        return SubscriptionsStore(redis=redis, initial_subscriptions=subscriptions)
    except JSONDecodeError as ex:
        logging.error(ex)
        logging.error('Could not load subscriptions from redis. Initializing with empty list instead')
        return SubscriptionsStore(redis=redis)


class SubscriptionsStore:
    _redis: Redis
    _subscriptions: List[Subscription] = []
    _lock: Lock = Lock()

    def __init__(self, redis: Redis, initial_subscriptions = None):
        self._redis = redis

        if initial_subscriptions:
            self._subscriptions = list(initial_subscriptions)

    def subscribe(self, chat_id: int, todoist_key: str):
        subscribed = any(sub.chat_id == chat_id for sub in self._subscriptions)
        if subscribed:
            return

        with self._lock:
            self._subscriptions.append(Subscription(chat_id, TodoistAPI(token=todoist_key, cache=None)))
            self._redis.lpush(redis_keys.subscription, dumps({'chat_id': chat_id, 'todoist_key': todoist_key}))

        logging.info(f'User with telegram id {chat_id} subcribed')

    def unsubscribe(self, chat_id):
        with self._lock:
            self._subscriptions = filter(lambda item: item.chat_id != chat_id, self._subscriptions)
        logging.info(f'User with telegram id {chat_id} unsubcribed')

    def get_subscriptions(self) -> Tuple[Subscription]:
        return tuple(self._subscriptions)
