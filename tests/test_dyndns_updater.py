from dyndns_updater import __version__
from unittest import TestCase
from dyndns_updater.updater import GandiUpdater, Updater
from dyndns_updater.extractor import Extractor
from unittest.mock import Mock, patch
import json
import pytest


class TestExtractor(TestCase):
    def test_(self):
        with open("./tests/out/response-2.json") as payload:
            filtered = Extractor._filter_records(
                json.load(payload), "serial", 1609351415
            )
            self.assertTrue(len(list(filtered)), 1)

    def test_2(self):
        with open("./tests/out/response-2.json") as payload:
            filtered = Extractor.extract_first_field_value(
                json.load(payload), "serial", 1609351415, "expire"
            )
            self.assertTrue(type(filtered), json)
            self.assertEqual(filtered, 604800)

    def test_multiplematch_raise_exception(self):
        with pytest.raises(ValueError):
            with open("./tests/out/multiple_match.json") as payload:
                filtered = Extractor.extract_first_field_value(
                    json.load(payload), "serial", 1609351415, "name"
                )


class TestGandiUpdater(TestCase):
    @patch("dyndns_updater.updater.requests.post")
    def test_constructor_inheritance(self, mock_get):

        normal_response = {
            "message": "Zone Created",
            "uuid": "ee788920-9bc5-11eb-823b-00163ea99cff",
        }

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = normal_response

        # updater = GandiUpdater('https://dns.api.gandi.net','some_key', 'somedomain.io', ['tower'])
        # self.assertEqual(updater.zone_uuid, "ee788920-9bc5-11eb-823b-00163ea99cff")

    @patch("dyndns_updater.updater.requests.get")
    def test_uuid_retreival(self, mock_get):
        with open("./tests/out/response-2.json") as payload:

            normal_response = json.load(payload)

            # mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = normal_response

            updater = GandiUpdater(
                "https://dns.api.gandi.net", "some_key", "somedomain.io", ["tower"]
            )

            self.assertEqual(updater.zone_uuid, "00163ee24379-089b3cc4-5b57-11e8-b297")