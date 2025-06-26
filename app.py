from flask import Flask
from deminer import create_app
import logging

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=5606)

