import os

from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    ENV: str = 'dev'

    LOG_DIR: str
    LOG_FILENAME: str
    LOG_LEVEL: str
    LOG_MBYTES: float
    LOG_BACKUP_COUNT: int

    WRITER_DB_URL: str
    READER_DB_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    class Config:
        case_sensitive = False
        env_file = 'dev.env'


class Dev(BaseConfig):
    ENV: str = 'dev'

    class Config:
        env_file = 'dev.env'


class Prod(BaseConfig):
    ENV: str = 'prod'

    class Config:
        env_file = 'prod.env'


def get_config():
    env = os.getenv("ENV", "dev")
    config_type = {
        "dev": Dev,
        "prod": Prod,
    }
    return config_type[env]()


config: BaseConfig = get_config()
