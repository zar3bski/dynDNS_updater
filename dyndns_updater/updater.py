import requests
import logging
import json
from dyndns_updater.extractor import Extractor

logger = logging.getLogger(__name__)


class Updater(object):
    def __init__(self, api_root, api_key, domain, subdomains):
        self.api_root = api_root
        self.api_key = api_key
        self.domain = domain
        self.subdomains = subdomains


class GandiUpdater(Updater):
    def __init__(self, *args, **kwargs):
        super(GandiUpdater, self).__init__(*args)
        self.zone_uuid = kwargs.get("zone_uuid") or self._get_zone_uuid()

    def _get_zone_uuid(self):
        response = requests.get(
            "{}/zones".format(self.api_root), headers={"X-Api-Key": self.api_key}
        )

        try:
            return Extractor.extract_first_field_value(
                response.json(), "name", self.domain, "uuid"
            )
        except:
            return self._generate_zone_uuid()

    def _generate_zone_uuid(self):
        response = requests.post(
            "{}/zones".format(self.api_root),
            data={"name": "{} zone".format(self.domain)},
            headers={"X-Api-Key": self.api_key},
        )

        try:
            return response.json()["uuid"]
        except Exception as e:
            logger.warn(
                "could not retreive zone uuid. HTTP status code {}: \n {}".format(
                    response.status_code, response.json
                )
            )
            raise e

    # TODO: find a way to deal with subdomains indicated in conf but not present in records

    def get_records(self):
        response = requests.get(
            "{}/zones/{}/records".format(self.api_root, self.zone_uuid),
            headers={"X-Api-Key": self.api_key},
        )

        a_records = Extractor.filter_items(response.json(), "rrset_type", ("A", "AAAA"))
        self.records = list(
            filter(lambda x: x["rrset_name"] in self.subdomains, a_records)
        )

    def check_and_update(self):
        pass