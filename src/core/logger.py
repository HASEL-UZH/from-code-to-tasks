import logging

from colorlog import ColoredFormatter


class LowerCaseLevelFormatter(ColoredFormatter):
    def format(self, record):
        record.levelname = record.levelname.lower()
        if record.levelno == logging.DEBUG:
            record.msg = f"\033[37m{record.msg}\033[39m"
        else:
            record.msg = f"\033[34m{record.msg}\033[39m"
        return super().format(record)


def setup_logger():
    logger = logging.getLogger("default")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = LowerCaseLevelFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            "trace": "grey",
            "debug": "cyan",
            "info": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


log = setup_logger()
log.debug("Logging initialized")
