from dyndns_updater import __version__
from unittest import TestCase
from dyndns_updater.updater import GandiUpdater, Updater
from dyndns_updater.extractor import Extractor
from unittest.mock import Mock, patch
import json
import pytest


class TestExtractor(TestCase):
    def test_(self):
        with open("./tests/out/gandi_zone_response.json") as payload:
            filtered = Extractor.filter_items(json.load(payload), "serial", 1609351415)
            self.assertEqual(len(list(filtered)), 1)

    def test_2(self):
        with open("./tests/out/gandi_zone_response.json") as payload:
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

    def test_filter_multiple_options(self):
        with open("./tests/out/gandi_records_response.json") as payload:
            filtered = list(
                Extractor.filter_items(json.load(payload), "rrset_type", ("A", "AAAA"))
            )
            self.assertEqual(len(filtered), 4)
            self.assertEqual(filtered[3].get('rrset_values'), ["a9f2:e357:31db:2a01:e0a:18d:c0:f416"])


class TestGandiUpdater(TestCase):
    @patch("dyndns_updater.updater.requests.get")
    def test_uuid_retreival(self, mock_get):
        with open("./tests/out/gandi_zone_response.json") as payload:

            normal_response = json.load(payload)

            # mock_get.return_value = Mock(ok=True)
            mock_get.return_value.json.return_value = normal_response

            updater = GandiUpdater(
                "https://fake.gandi.net", "some_key", "somedomain.io", ["tower"]
            )

            self.assertEqual(updater.zone_uuid, "00163ee24379-089b3cc4-5b57-11e8-b297")

    @patch("dyndns_updater.updater.requests.get")
    @patch("dyndns_updater.updater.requests.post")
    def test_constructor_inheritance(self, mock_post, mock_get):

        get_response = [{"message": "no zone UUID attached to domain"}]

        create_response = {
            "message": "Zone Created",
            "uuid": "ee788920-9bc5-11eb-823b-00163ea99cff",
        }

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = get_response

        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = create_response

        updater = GandiUpdater(
            "https://fake.gandi.net", "some_key", "somedomain.io", ["tower"]
        )
        self.assertEqual(updater.zone_uuid, "ee788920-9bc5-11eb-823b-00163ea99cff")
