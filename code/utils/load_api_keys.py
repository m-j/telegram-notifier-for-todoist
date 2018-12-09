import logging
import sys
import json


def load_config():
    if len(sys.argv) == 2:
        path = sys.argv[1]

        try:
            with open(path, 'r') as content_file:
                content = json.loads(content_file.read())
                return content
        except:
            logging.exception('Could not open configuration file')
    else:
        logging.error('No configuration file specified as commandline param')
        return None