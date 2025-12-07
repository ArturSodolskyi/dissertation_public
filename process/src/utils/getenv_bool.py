import os


def getenv_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "y")


DEBUG = getenv_bool("DEBUG", default=False)
