import configparser
import pathlib
import logging
import shutil
import functools
from ast import literal_eval

logger = logging.getLogger('scrap_logger')


def load_config(file='config.ini', delete_config=False):
    # check if config file exists
    abs_file = pathlib.Path.cwd() / file
    if delete_config:
        logger.warning("Deleting config file")
        if abs_file in pathlib.Path.cwd().iterdir():
            pathlib.Path.unlink(abs_file)
    if abs_file not in pathlib.Path.cwd().iterdir():
        logger.warning("Config file " + file + " not found!")
        template = pathlib.Path.cwd() / pathlib.Path('template_' + file)
        logger.warning("Trying to create config file from template " + str(template))
        # if config file is missing a default config is created from the template
        if template not in pathlib.Path.cwd().iterdir():
            logger.error("Config template file " + str(template) + " not found!")
        else:
            shutil.copy(str(template), str(abs_file))

            logger.info("Created config file from template.")
    config = configparser.ConfigParser(interpolation=None)
    config.read(file)

    return config


config = load_config(delete_config=True)


def try_getter(func):
    # decorator to try getter
    @functools.wraps(func)
    def wrapper_try_getter(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except configparser.Error as e:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.error(f"Unable to call getter: {func.__name__}({signature})")
            logger.debug(e)
            return
        except KeyError as e:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.error(f"Unable to call getter: {func.__name__}({signature})")
            logger.debug(e)
            return
    return wrapper_try_getter


def try_setter(func):
    # decorator to try setter
    @functools.wraps(func)
    def wrapper_try_setter(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return
        except configparser.Error as e:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.error(f"Unable to call setter: {func.__name__}({signature})")
            logger.debug(e)
        except KeyError as e:
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.error(f"Unable to call setter: {func.__name__}({signature})")
            logger.debug(e)
    return wrapper_try_setter


@try_getter
def blank_getter(section, option):
    # allows to directly access an option by section and option
    return config[section][option]


@try_getter
def get_regions():
    # returns the list of regions
    return literal_eval(config["GENERAL"]["REGIONS"])


@try_getter
def get_websites():
    return literal_eval(config["GENERAL"]["WEBSITES"])


@try_getter
def get_timezone():
    return config["GENERAL"]["TIMEZONE"]


@try_getter
def get_battlefy_url(region):
    return config["BATTLEFY"][str(region + "_URL")]


@try_getter
def get_battlefy_time_frame():
    return config["BATTLEFY"]["TIME_FRAME"]


# TODO add more setter


@try_setter
def blank_setter(section, option, value):
    # allows to directly change an option by section and option
    config.set(section, option, value)
