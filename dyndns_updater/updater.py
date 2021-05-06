import logging
from abc import abstractmethod, ABC
import requests
from dyndns_updater.extractor import Extractor


logging.basicConfig(level=logging.INFO)


class Updater(ABC):
    def __init__(self, api_root, credentials, domain, subdomains, locator):
        self.api_root = api_root
        self.credentials = credentials
        self.domain = domain
        self.subdomains = subdomains
        self.locator = locator

    def __str__(self):
        return "{}::{}".format(type(self), self.domain)

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def check_and_update(self):
        pass

    @classmethod
    def factory(cls, config, locator):
        """Generates a pool of updater based of the provided config object"""
        pool = []
        for provider in config.dns_providers:
            # just complete this enumeration if new providers are created
            if "gandi" in provider.keys():
                for (domain, subdomains) in filter(
                    lambda x: x[0] != "gandi", provider.items()
                ):
                    pool.append(
                        GandiUpdater(
                            "https://api.gandi.net/v5/livedns",
                            provider["gandi"],
                            domain,
                            list(subdomains.items()),
                            locator,
                        )
                    )
        logging.info(
            "Running using the following updaters: {}".format([str(x) for x in pool])
        )
        return pool


class GandiUpdater(Updater):
    def initialize(self):
        self._get_records()
        self._record_missing()

    def _get_records(self):
        response = requests.get(
            "{}/domains/{}/records".format(self.api_root, self.domain),
            headers={"Authorization": "Apikey {}".format(self.credentials)},
        )
        if response.status_code == 200:
            a_records = Extractor.filter_items(
                response.json(), "rrset_type", ("A", "AAAA")
            )
            self.records = list(
                filter(
                    lambda x: x["rrset_name"] in [t[0] for t in self.subdomains],
                    a_records,
                )
            )
        else:
            logging.error(
                "Failed to retreive records for {}\n Api response: {}".format(
                    self.domain, response.json()
                )
            )

    def _record_missing(self):
        missing = filter(
            lambda x: x[0] not in [y["rrset_name"] for y in self.records],
            self.subdomains,
        )
        new_records = [
            {
                "rrset_type": "{}".format(subdomain[1]),
                "rrset_name": "{}".format(subdomain[0]),
                "rrset_values": [
                    "{}".format(
                        self.locator.local_ipv4
                        if subdomain[1] == "A"
                        else self.locator.local_ipv6
                    )
                ],
                "rrset_ttl": 1800,
            }
            for subdomain in missing
        ]
        if new_records != []:
            for record in new_records:
                response = requests.post(
                    "{}/domains/{}/records".format(self.api_root, self.domain),
                    headers={"Authorization": "Apikey {}".format(self.credentials)},
                    json=record,
                )
                if response.status_code == 201 or response.status_code == 200:
                    logging.info(
                        "{} successfully recorded!".format(record["rrset_name"])
                    )
                    self.records.append(record)
                else:
                    logging.warning(
                        "failed to record {} ({}). Reason: {}".format(
                            record["rrset_name"],
                            response.status_code,
                            response.text,
                        )
                    )

    def check_and_update(self):
        ipv4 = self.locator.local_ipv4
        ipv6 = self.locator.local_ipv6

        def _update_and_log(record, new_ip):
            try:
                response = requests.put(
                    "{}/domains/{}/records/{}/{}".format(
                        self.api_root,
                        self.domain,
                        record["rrset_name"],
                        record["rrset_type"],
                    ),
                    headers={"Authorization": "Apikey {}".format(self.credentials)},
                    json={"rrset_ttl": 1800, "rrset_values": ["{}".format(new_ip)]},
                )
                if response.status_code == 201:
                    logging.info("{} updated with success".format(record["rrset_name"]))
                    record["rrset_values"][0] = new_ip
                else:
                    logging.warning(
                        "Could not update {} ({}): {}".format(
                            record["rrset_name"], response.status_code, response.text
                        )
                    )
            except Exception as e:
                logging.error(
                    "Could not update {} Reason: {}".format(record["rrset_name"], e)
                )

        for record in self.records:
            if record["rrset_type"] == "A" and record["rrset_values"][0] != ipv4:
                _update_and_log(record, ipv4)
            elif record["rrset_type"] == "AAAA" and record["rrset_values"][0] != ipv6:
                _update_and_log(record, ipv6)
