import requests
import logging
import json
from dyndns_updater.extractor import Extractor
from abc import abstractmethod, ABC

logging.basicConfig(level=logging.INFO)


class Updater(ABC):
    def __init__(self, api_root, credentials, domain, subdomains):
        self.api_root = api_root
        self.credentials = credentials
        self.domain = domain
        self.subdomains = subdomains

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def check_and_update(self):
        pass

    @classmethod
    def factory(cls, config):
        pool = []
        for provider in config.dns_providers:
            # just complete this enumeration if new providers are created
            if "gandi" in provider.keys():
                for (domain, subdomains) in filter(
                    lambda x: x[0] != "gandi", provider.items()
                ):
                    pool.append(
                        GandiUpdater(
                            "https://dns.api.gandi.net/api/v5",
                            provider["gandi"],
                            domain,
                            list(subdomains.items()),
                        )
                    )
        return pool


class GandiUpdater(Updater):
    def __init__(self, *args, **kwargs):
        super(GandiUpdater, self).__init__(*args)

    def initialize(self):
        self._get_zone_uuid()
        self._get_records()

    def _get_zone_uuid(self):
        response = requests.get(
            "{}/zones".format(self.api_root), headers={"X-Api-Key": self.credentials}
        )

        try:
            self.zone_uuid = Extractor.extract_field_value(
                response.json(), "name", self.domain, "uuid"
            )

        except:
            return self._generate_zone_uuid()

    def _generate_zone_uuid(self):
        response = requests.post(
            "{}/zones".format(self.api_root),
            data={"name": "{} zone".format(self.domain)},
            headers={"X-Api-Key": self.credentials},
        )

        try:
            self.zone_uuid = response.json()["uuid"]
        except Exception as e:
            logging.warn(
                "could not retreive zone uuid. HTTP status code {}: \n {}".format(
                    response.status_code, response.json
                )
            )
            raise e

    # TODO: find a way to deal with subdomains indicated in conf but not present in records
    def _get_records(self):
        response = requests.get(
            "{}/zones/{}/records".format(self.api_root, self.zone_uuid),
            headers={"X-Api-Key": self.credentials},
        )

        a_records = Extractor.filter_items(response.json(), "rrset_type", ("A", "AAAA"))
        self.records = list(
            filter(lambda x: x["rrset_name"] in self.subdomains, a_records)
        )

    def check_and_update(self):
        pass
