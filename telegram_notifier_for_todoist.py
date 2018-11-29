from notifications_watch.notifications_watcher import NotificationsWatcher
from notifications_watch.pending_notifications_store import PendingNotificationsStore
from utils.load_api_keys import load_api_keys

api_keys = load_api_keys()
todist_api_key = api_keys['todoist_api_key']


def main():
    pending_notifications_store = PendingNotificationsStore()
    # notifications_watcher = NotificationsWatcher(todoist_api_key=todist_api_key,
    #                                              pending_notifications_store=pending_notifications_store)
    # notifications_watcher.start()


main()