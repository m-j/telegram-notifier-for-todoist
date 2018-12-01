from dataclasses import dataclass
from queue import Queue
from threading import Thread

import todoist


@dataclass(frozen=True)
class SyncOrder:
    todoist_api: todoist.TodoistAPI
    telegram_id: int

class NotificationSyncScheduler:
    enabled: bool
    thread: Thread
    queue: Queue = Queue()

    def __init__(self):
        pass

    def _run(self):
        pass
        # while self.enabled:



    def start(self):
        self.enabled = True
        self.thread.start()

    def stop(self):
        self.enabled = False
        self.thread.join(5)