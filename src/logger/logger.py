import logging
import os
from logging import handlers
import time

class ColorFormatter(logging.Formatter):
    grey = "\033[37m"
    green = "\033[32m"
    yellow = "\033[33m"
    red = "\033[31m"
    bold_red = "\033[1;31m"
    reset = "\033[0m"
    format_str = "%(asctime)s - %(levelname)-8s - [%(filename)s:%(funcName)s] - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset,
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
        return formatter.format(record)

# 1. 创建 __logger 主体
__logger = logging.getLogger("JarvisLogger")
__logger.setLevel(logging.DEBUG)  # 总入口必须最低级别
__logger.propagate = False  # 防止重复打印

# 2. 定义处理器
# ----------------------
# 控制台 Handler (LOG_LEVEL)
# ----------------------
console_handler = logging.StreamHandler()
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
console_handler.setLevel(log_level)
console_handler.setFormatter(ColorFormatter())
__logger.addHandler(console_handler)
# ----------------------
# 文件 Handler DEBUG+ (LOG_DIR)
# ----------------------
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s - [%(filename)s:%(funcName)s] - %(message)s")
log_dir = os.getenv("LOG_DIR", "logs")
os.makedirs(log_dir, exist_ok=True)
log_name = time.strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(log_dir, log_name)
file_handler = handlers.RotatingFileHandler(
    log_path,
    maxBytes=5 * 1024 * 1024,  # 5M
    backupCount=3,
    encoding="utf-8",
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
__logger.addHandler(file_handler)

# 3. 清理旧日志文件 (LOG_RETENTION)
log_retention = int(os.getenv("LOG_RETENTION", 7))
now = time.time()
for filename in os.listdir(log_dir):
    if filename.endswith(".log"):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_age_days = (now - os.path.getmtime(file_path)) / (24 * 3600)
            if file_age_days > log_retention:
                os.remove(file_path)

def debug(message: str) -> None:
    __logger.debug(message, stacklevel=2)

def info(message: str | bool) -> None:
    __logger.info(message, stacklevel=2)

def warning(message: str) -> None:
    __logger.warning(message, stacklevel=2)

def error(message: str) -> None:
    __logger.error(message, stacklevel=2)

def critical(message: str) -> None:
    __logger.critical(message, stacklevel=2)
        
if __name__ == "__main__":
    __logger.debug("This is a debug message.")
    __logger.info("This is an info message.")
    __logger.warning("This is a warning message.")
    __logger.error("This is an error message.")
    __logger.critical("This is a critical message.")