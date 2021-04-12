import requests
import logging

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
        self.zone_uuid = self._get_zone_uuid()

    def _get_zone_uuid(self):
        response = requests.post(
            "{}/zones".format(self.api_root),
            data={"name": "{} zone".format(self.domain)},
            headers={
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json; charset=UTF-8",
            },
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

    def check_and_update(self):
        pass