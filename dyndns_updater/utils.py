from threading import Lock
import logging
import yaml

logging.basicConfig(level=logging.INFO)


class SingletonMeta(type):
    """
    thread-safe implementation of Singleton.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self, ip_identifier, delta, dns_providers):
        self.ip_identifier = ip_identifier
        self.delta = delta
        self.dns_providers = dns_providers

    def __del__(self):
        pass

    @classmethod
    def factory(cls, path):
        with open(path) as file:
            doc = yaml.load(file, Loader=yaml.FullLoader)
            return Config(doc["ip_identifier"], doc["delta"], doc["dns_providers"])
