import configparser
import pathlib
import logging
import shutil
import functools


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


def update_config(func):
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
    # allows to directly access an option by section and option
    return config[section][option]


@try_config()
def get_regions():
    # returns the list of regions
    return config["GENERAL"]["REGIONS"].split(",")


@try_config()
def get_websites():
    return config["GENERAL"]["WEBSITES"].split(",")


@try_config()
def get_timezone():
    return config["GENERAL"]["TIMEZONE"]


@try_config()
def get_battlefy_url(region):
    return config["BATTLEFY"][str(region + "_URL")]


@try_config()
def get_battlefy_time_frame():
    return config["BATTLEFY"]["TIME_FRAME"]


@update_config
@try_config(is_getter=False)
def blank_setter(section, option, value):
    # allows to directly change an option by section and option
    config.set(section, option, value)


@update_config
@try_config(is_getter=False)
def set_regions(regions):
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
    if isinstance(timezone, (str, )):
        config.set("GENERAL", "TIMEZONE", timezone)
    else:
        logger.error("Can't change timezone config, given value has the wrong type")
        logger.debug("given type: " + str(type(timezone)) + " required: 'str'")


@update_config
@try_config(is_getter=False)
def set_battlefy_url(url, region):
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
    if isinstance(frame, (str, )):
        possible_frames = ["TODAY", "THIS_WEEK", "THIS_WEEKEND"]
        if frame in possible_frames:
            config.set("BATTLEFY", "TIME_FRAME", frame)
        else:
            logger.error("Can't change battlefy time frame, given value " + frame + " is not in " + str(possible_frames))
    else:
        logger.error("Can't change battlefy time frame config, given value has the wrong type")
        logger.debug("given type: " + str(type(frame)) + " required: 'list'")
