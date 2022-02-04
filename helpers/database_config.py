from configparser import ConfigParser
from typing import List, Dict, Tuple

def database_config(filename, section="postgresql"):
    # Create Parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db: Dict[str, str] = dict()
    if parser.has_section(section):
        params: List[Tuple[str, str]] = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
            # print(param)
    else:
        raise Exception('Section {0} is not found in {1} file'.format(section, filename))
    return db