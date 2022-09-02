import sys
import os
import loguru

from core.config import config

debugger = loguru.logger


def init_logger():
    log_format = '[{time:YYYY-MM-DD HH:mm:ss.SSS}] [{process: >5}] [{level.name:>5}] <level>{message}</level>'
    loguru.logger.configure(
        handlers=[
            dict(sink=sys.stdout,
                 format=log_format,
                 level=config.LOG_LEVEL.upper(),
                 colorize=True),
            dict(sink=os.path.join(config.LOG_DIR, config.LOG_FILENAME),
                 format=log_format,
                 enqueue=True,
                 level=config.LOG_LEVEL.upper(),
                 # serialize=True,
                 rotation='%s MB' % config.LOG_MBYTES,
                 retention=config.LOG_BACKUP_COUNT,
                 )
        ],
    )
