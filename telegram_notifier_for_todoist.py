from notifications_watch.notifications_watcher import NotificationsWatcher
from utils.load_api_keys import load_api_keys
import asyncio

api_keys = load_api_keys()
todist_api_key = api_keys['todoist_api_key']

async def main():
    notifications_watcher = NotificationsWatcher(todist_api_key)
    await notifications_watcher.run()

asyncio.run(main(), debug=True)