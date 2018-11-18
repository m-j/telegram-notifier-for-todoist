from notifications_watch.notifications_watcher import NotificationsWatcher
from utils.load_api_keys import load_api_keys
from threading import Thread

api_keys = load_api_keys()
todist_api_key = api_keys['todoist_api_key']


def main():
    notifications_watcher = NotificationsWatcher(todist_api_key)
    notifications_watcher.start()


main()