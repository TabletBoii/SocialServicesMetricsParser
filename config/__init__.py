import yaml
from yaml.loader import SafeLoader
import os

FILE: str = os.path.dirname(os.path.abspath(__file__)) + '/dev.yaml'

with open(FILE) as f:
    config = yaml.load(f, Loader=SafeLoader)

__all__ = [
    "config"
]
