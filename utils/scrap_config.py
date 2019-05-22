"""
Handles the config file.
This module needs to be imported into other modules in oder to access config.
:author: Jonathan Decker
"""

import configparser
import pathlib
import logging
import shutil
import functools
import pytz
from os import environ


logger = logging.getLogger('scrap_logger')


def load_config(file='config.ini', delete_config=False):
    """
    Loads configs or recreates it from the template.
    :param file: String, the name of the config file, usually config.ini
    :param delete_config: Boolean, if True config file is deleted and recreated from the template
    :return: Configparser, the parser has read the config file and handles the live config
    """

    # check if Travis is active
    travis = False
    try:
        travis = environ['TRAVIS']
    except:
        pass

    # check if config file exists
    if travis:
        abs_path = environ['TRAVIS_BUILD_DIR']
    else:
        abs_path = pathlib.Path.cwd()
    abs_file = abs_path / file
    if delete_config:
        logger.warning("Deleting config file.")
        if abs_file in abs_path.iterdir():
            pathlib.Path.unlink(abs_file)
            logger.info("Deleted config file.")
        else:
            logger.warning("Failed to delete config file.")
    if abs_file not in abs_path.iterdir():
        logger.warning("Config file " + file + " not found!")
        template = abs_path / pathlib.Path('template_' + file)
        logger.warning("Trying to create config file from template " + str(template))
        # if config file is missing a default config is created from the template
        if template not in abs_path.iterdir():
            logger.error("Config template file " + str(template) + " not found!")
            logger.error(*abs_path.iterdir())
        else:
            shutil.copy(str(template), str(abs_file))

            logger.info("Created config file from template.")
    config = configparser.ConfigParser(interpolation=None)
    config.read(file)

    return config


# delete config can be set for debugging purposes
config = load_config()


def update_config(func):
    """
    Wrapper that updates the config file with the live config
    :param func: func, a function that made any changes to the live config
    :return: wrapper_update_config
    """

    @functools.wraps(func)
    # updates the config.ini file upon changing a config
    def wrapper_update_config(*args, **kwargs):
        value = func(*args, **kwargs)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            logger.debug("Updated config.ini")
        return value
    return wrapper_update_config


def try_config(is_getter=True):
    """
    Decorator for the wrapper that catches configparser error and keyerror while getting or setting configs.
    :param is_getter: Boolean, helps selecting the error message
    :return: decorator_try_config
    """

    def decorator_try_config(func):
        # decorator to try config
        @functools.wraps(func)
        def wrapper_try_config(*args, **kwargs):
            try:
                value = func(*args, **kwargs)
                return value
            except configparser.Error as e:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                if is_getter:
                    logger.error(f"Unable to call getter: {func.__name__}({signature})")
                else:
                    logger.error(f"Unable to call setter: {func.__name__}({signature})")
                logger.debug(e)
                return
            except KeyError as e:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                if is_getter:
                    logger.error(f"Unable to call getter: {func.__name__}({signature})")
                else:
                    logger.error(f"Unable to call setter: {func.__name__}({signature})")
                logger.debug(e)
                return
        return wrapper_try_config
    return decorator_try_config


@try_config()
def blank_getter(section, option):
    """
    Allow direct access to any option. ONLY USED FOR TESTING!
    :param section: String, a valid config section
    :param option: String, a valid option in the given section
    :return: String, value of the given section and option
    """

    # allows to directly access an option by section and option
    return config[section][option]


@try_config()
def get_region():
    """
    Returns the region as string
    :return: String, contains the current region
    """

    return config["GENERAL"]["REGION"]


@try_config()
def get_timezone():
    """
    Returns the time zone set in the config.
    :return: String, should be compatible with pytz package
    """

    return config["GENERAL"]["TIMEZONE"]


@update_config
@try_config(is_getter=False)
def blank_setter(section, option, value):
    """
    Allows directly changing a specific option. ONLY USED FOR TESTING!
    :param section: String, a valid section in the config
    :param option: String, a valid option in the given section
    :param value: String, the new value
    :return: None, but config is updated
    """

    # allows to directly change an option by section and option
    config.set(section, option, value)


@update_config
@try_config(is_getter=False)
def set_region(region):
    """
    Set region to a given string, for example "EUW"
    :param region: String, the abbreviation of the selected Region
    :return: None, but config is updated
    """

    if isinstance(region, str):
        config.set("GENERAL", "REGION", region)
        logger.info("Config region has been updated to " + get_region())
    else:
        logger.error("Can't change region config, given value has the wrong type")
        logger.debug("given type: " + str(type(region)) + " required: 'str'")


@update_config
@try_config(is_getter=False)
def set_timezone(timezone):
    """
    Set timezone to a given String
    :param timezone: String, needs to be a valid timezone in pytz
    :return: None, but config is updated
    """

    if isinstance(timezone, (str, )):
        if timezone in pytz.all_timezones:
            config.set("GENERAL", "TIMEZONE", timezone)
            logger.info("Config timezone has been updated to " + get_timezone())
        else:
            logger.error("Can't change timezone config, given value is not a valid timezone")
            logger.debug("given value: " + timezone)
    else:
        logger.error("Can't change timezone config, given value has the wrong type")
        logger.debug("given type: " + str(type(timezone)) + " required: 'str'")
