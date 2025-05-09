from flask import Flask
from deminer import create_app


if __name__ == '__main__':
    create_app().run()