import pathlib
import logging
import logging.config
import time
from os import listdir


def setup_logger(console_level=logging.DEBUG, log_file_level=logging.DEBUG, logs_to_keep=20):
    # create logger with 'scrap_logger'
    scrap_logger = logging.getLogger('scrap_logger')
    scrap_logger.setLevel(logging.DEBUG)

    # create file handler
    path_to_logs = pathlib.Path.cwd() / "logs"
    # check if logs folder exists and create it if needed
    if not (path_to_logs.exists() and path_to_logs.is_dir()):
        path_to_logs.mkdir()
    # if more then 20 files are in the
    if len(listdir(path_to_logs)) > logs_to_keep:
        for i in range(0, 5):
            delete_oldest_log(path_to_logs)
    time_str = time.strftime("%d-%m-%Y_%H-%M-%S")
    log_file_name = "log_" + time_str + ".log"
    fh = logging.FileHandler(path_to_logs / log_file_name)
    fh.setLevel(log_file_level)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    scrap_logger.addHandler(fh)
    scrap_logger.addHandler(ch)

    scrap_logger.info("Finished setting up logger.")

    return scrap_logger


def delete_oldest_log(path_to_logs):
    if len(listdir(path_to_logs)) == 0:
        return
    time, file_path = min((f.stat().st_mtime, f) for f in path_to_logs.iterdir())
    pathlib.Path.unlink(file_path)
