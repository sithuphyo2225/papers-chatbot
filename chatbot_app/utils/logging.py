from logging import getLogger


def get_logger(name):
    return getLogger(name)


def get_app_logger():
    return get_logger("app")
