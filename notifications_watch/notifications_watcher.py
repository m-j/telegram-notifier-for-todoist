import todoist
import asyncio
from datetime import datetime, timezone

date_time_format = '%a %d %b %Y %H:%M:%S %z'

class NotificationsWatcher:
    api : todoist.TodoistAPI
    enabled: bool

    def __init__(self, todoist_api_key:str):
        self.api = todoist.TodoistAPI(todoist_api_key)
        self.enabled = False

    async def run(self):
        self.enabled = True

        while self.enabled:
            sync_response = self.api.sync()
            if 'http_code' in sync_response and sync_response['http_code'] > 300:
                raise Exception('Failed to sync ' + str(sync_response))

            reminders = self.api.reminders.all()

            aware_now = datetime.now(timezone.utc)

            # api does not contain reminders from past
            # we'll have to look for reminders that will be in past within some interval (like 10 minutes

            passed_reminders = [
                reminder for reminder in reminders if aware_now >= datetime.strptime(reminder.data['due_date_utc'], date_time_format)
            ]

            print(passed_reminders)

            await asyncio.sleep(5)

            self.enabled = False