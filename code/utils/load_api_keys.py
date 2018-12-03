import sys
import json


def load_config():
    if len(sys.argv) == 2:
        path = sys.argv[1]
        with open(path, 'r') as content_file:
            content = json.loads(content_file.read())
            return content
    else:
        return None