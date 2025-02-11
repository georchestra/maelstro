from collections import namedtuple
from dataclasses import dataclass


Credentials = namedtuple("Credentials", ["login", "password"])

GsLayer = namedtuple("GsLayer", ["workspace_name", "layer_name"])
GsLayer.__str__ = lambda l: ":".join(el for el in l if el is not None)  # type: ignore


@dataclass
class DbConfig:
    host: str = "database"
    port: int = 5432
    login: str = "georchestra"
    password: str = "georchestra"
    database: str = "georchestra"
    schema: str = "maelstro"
    table: str = "logs"
