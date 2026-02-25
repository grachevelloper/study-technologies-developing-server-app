from dataclasses import dataclass
from environs import Env
from typing import Optional


@dataclass
class DatabaseConfig:
    database_url: Optional[str] = None


@dataclass
class Config:
    db: DatabaseConfig
    secret_key: str
    debug: bool


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    
    try:
        database_url = env("DATABASE_URL")
    except:
        database_url = None
    
    return Config(
        db=DatabaseConfig(database_url=database_url),
        secret_key=env("SECRET_KEY", "default-secret-key"),
        debug=env.bool("DEBUG", default=False)
    )