import logging
import os


def log_action(message, level, log_file):
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(log_file)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    elif level == "critical":
        logger.critical(message)
    else:
        logger.info(message)


def log_general_action(message, level):
    log_action(message, level, "logs/general.log")


def log_admin_action(message, level):
    log_action(message, level, "logs/admin.log")


def log_instructor_action(message, level):
    log_action(message, level, "logs/instructor.log")


def log_student_action(message, level):
    log_action(message, level, "logs/student.log")