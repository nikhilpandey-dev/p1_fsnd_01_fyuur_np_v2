from .database_config import database_config
from typing import List, Dict, Tuple


def sqlalchemy_config(filename: str) -> str:
    params: Dict[str, str] = database_config(filename = filename)
    # print('Database credentials are: ')
    database_credeintials_config: str = (f"{params['dialect']}://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}")
    # print(database_credeintials_config)
    return database_credeintials_config