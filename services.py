import logging
from logging.handlers import RotatingFileHandler


def logging_service(logger_name, log_id=None):
    """
    :param log_id:
    :param logger_name:
    :return: logger object with rotate file handler
    """
    global loggers

    if loggers.get(logger_name):
        return loggers.get(logger_name)
    else:
        log_format = '%(asctime)s [%(levelname)s] [hbs-backend-api] %(message)s [(%(filename)s : %(lineno)d)]'
        if log_id:
            log_format = '%(asctime)s [%(levelname)s] [hbs-backend-api] [{}]%(message)s [(%(filename)s : %(lineno)d)]'. \
                format(log_id)
        log_level = logging.DEBUG

        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        logger.propagate = False

        # create file handler
        log_file_name = './logs/{}.log'.format(logger_name)
        file_handler = RotatingFileHandler(log_file_name, mode='a', maxBytes=30 * 1024 * 1024, backupCount=1)
        file_handler.setLevel(log_level)

        # create stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(log_level)

        # create formatter and add it to the handlers
        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # add the handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger
