from collections import namedtuple


Credentials = namedtuple("Credentials", ["login", "password"])

GsLayer = namedtuple("GsLayer", ["workspace_name", "layer_name"])
GsLayer.__str__ = lambda l: ":".join(el for el in l if el is not None)
