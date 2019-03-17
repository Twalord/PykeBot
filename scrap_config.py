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


logger = logging.getLogger('scrap_logger')


def load_config(file='config.ini', delete_config=False):
    """
    Loads configs or recreates it from the template.
    :param file: String, the name of the config file, usually config.ini
    :param delete_config: Boolean, if True config file is deleted and recreated from the template
    :return: Configparser, the parser has read the config file and handles the live config
    """

    # check if config file exists
    abs_file = pathlib.Path.cwd() / file
    if delete_config:
        logger.warning("Deleting config file.")
        if abs_file in pathlib.Path.cwd().iterdir():
            pathlib.Path.unlink(abs_file)
            logger.info("Deleted config file.")
        else:
            logger.warning("Failed to delete config file.")
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
def get_regions():
    """
    Returns a list of all regions selected.
    :return: List[String], containing the regions
    """

    # returns the list of regions
    return config["GENERAL"]["REGIONS"].split(",")


@try_config()
def get_websites():
    """
    Retunrs a list of all websites selected.
    :return: List[String], containing the websites
    """

    return config["GENERAL"]["WEBSITES"].split(",")


@try_config()
def get_timezone():
    """
    Returns the time zone set in the config.
    :return: String, should be compatible with pytz package
    """

    return config["GENERAL"]["TIMEZONE"]


@try_config()
def get_battlefy_url(region):
    """
    Returns the battlefy url for the given region.
    :param region: String, must be a valid region from the config
    :return: String, the url set in the config for the given region
    """

    return config["BATTLEFY"][str(region + "_URL")]


@try_config()
def get_battlefy_time_frame():
    """
    Returns the time frame selected in the config.
    :return: String, possible time frames are "TODAY", "THIS_WEEK", "THIS_WEEKEND"
    """

    return config["BATTLEFY"]["TIME_FRAME"]


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
def set_regions(regions):
    """
    Set regions to a given list of regions, for example "EUW"
    :param regions: List[String], a list of regions
    :return: None, but config is updated
    """

    if isinstance(regions, (list, )):
        region_string = ""
        for item in regions:
            region_string += item + ","
        region_string = region_string[:-1]
        config.set("GENERAL", "REGIONS", region_string)
    else:
        logger.error("Can't change regions config, given value has the wrong type")
        logger.debug("given type: " + str(type(regions)) + " required: 'list'")
    return get_regions()


@update_config
@try_config(is_getter=False)
def set_websites(websites):
    """
    Set websites to a given list of websites, for example "Battlefy"
    :param websites: List[String], a list of websites
    :return: None, but config is updated
    """

    if isinstance(websites, (list, )):
        websites_string = ""
        for item in websites:
            websites_string += item + ","
        websites_string = websites_string[:-1]
        config.set("GENERAL", "WEBSITES", websites_string)
    else:
        logger.error("Can't change websites config, given value has the wrong type")
        logger.debug("given type: " + str(type(websites)) + " required: 'list'")


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
        else:
            logger.error("Can't change timezone config, given value is not a valid timezone")
            logger.debug("given value: " + timezone)
    else:
        logger.error("Can't change timezone config, given value has the wrong type")
        logger.debug("given type: " + str(type(timezone)) + " required: 'str'")


@update_config
@try_config(is_getter=False)
def set_battlefy_url(url, region):
    """
    Set the battlefy url to a given string for a given region
    :param url: String, should be a valid url for the battlefy search page
    :param region: String, should be a valid region from the regions config
    :return: None, but config is updated
    """

    if isinstance(url, (str, )) and isinstance(region, (str, )):
        if not config.has_option("BATTLEFY", str(region + "_URL")):
            logger.debug("adding option [BATTLEFY][" + str(region + "_URL") + "]")
        config.set("BATTLEFY", str(region + "_URL"), url)
    else:
        logger.error("Can't change battlefy url config, given value has the wrong type")
        logger.debug("given type: " + str(type(url)) + " " + str(type(region)) + " required: 'str' 'str'")


@update_config
@try_config(is_getter=False)
def set_battlefy_time_frame(frame):
    """
    Set the battlefy time frame to be used.
    :param frame: String, must be "TODAY", "THIS_WEEK" or "THIS_WEEKEND"
    :return: None, but config is updated
    """

    if isinstance(frame, (str, )):
        possible_frames = ["TODAY", "THIS_WEEK", "THIS_WEEKEND"]
        if frame in possible_frames:
            config.set("BATTLEFY", "TIME_FRAME", frame)
        else:
            logger.error("Can't change battlefy time frame, given value " + frame + " is not in " + str(possible_frames))
    else:
        logger.error("Can't change battlefy time frame config, given value has the wrong type")
        logger.debug("given type: " + str(type(frame)) + " required: 'list'")
