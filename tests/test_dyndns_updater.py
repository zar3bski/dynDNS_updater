from dyndns_updater import __version__
from unittest import TestCase
from dyndns_updater.locator import Locator
from dyndns_updater.utils import Config, SingletonMeta
from dyndns_updater.updater import GandiUpdater, Updater
from dyndns_updater.extractor import Extractor
from unittest.mock import Mock, patch, PropertyMock, MagicMock
import json
import pytest
import gc
import re


class TestConfig(TestCase):
    def tearDown(self):
        instances = [obj for obj in gc.get_objects() if isinstance(obj, Config)]
        for i in instances:
            del i

    def test_factory_simple_example(self):
        conf = Config.factory("./tests/confs/two_domains.yaml")
        self.assertEqual(conf.ip_identifier, "cloudflare")
        self.assertEqual(conf.delta, 900)
        self.assertEqual(
            conf.dns_providers,
            [
                {
                    "gandi": "some_key",
                    "somedomain.io": {"infra3": "AAAA", "infra": "A"},
                    "someotherdomain.io": {"blog": "A"},
                }
            ],
        )

    # FIXME: find a decent way to test this Singleton based class

    # def test_factory_multiple(self):
    #    #mocker.patch.dict(SingletonMeta, '_instances', clear=True)
    #    conf = Config.factory("tests/confs/two_dns_providers.yaml")
    #    self.assertEqual(len(conf.dns_providers),2)


class TestExtractor(TestCase):
    def test_(self):
        with open("./tests/out/gandi_zone_response.json") as payload:
            filtered = Extractor.filter_items(json.load(payload), "serial", 1609351415)
            self.assertEqual(len(list(filtered)), 1)

    def test_2(self):
        with open("./tests/out/gandi_zone_response.json") as payload:
            filtered = Extractor.extract_field_value(
                json.load(payload), "serial", 1609351415, "expire"
            )
            self.assertTrue(type(filtered), json)
            self.assertEqual(filtered, 604800)

    def test_multiplematch_raise_exception(self):
        with pytest.raises(ValueError):
            with open("./tests/out/multiple_match.json") as payload:
                Extractor.extract_field_value(
                    json.load(payload), "serial", 1609351415, "name"
                )

    def test_filter_multiple_options(self):
        with open("./tests/out/gandi_records_response.json") as payload:
            filtered = list(
                Extractor.filter_items(json.load(payload), "rrset_type", ("A", "AAAA"))
            )
            self.assertEqual(len(filtered), 4)
            self.assertEqual(
                filtered[3].get("rrset_values"), ["a9f2:e357:31db:2a01:e0a:18d:c0:f416"]
            )

    def test_filter_multiple_options_more(self):
        with open("./tests/out/gandi_records_response.json") as payload:
            filtered = list(
                Extractor.filter_items(
                    json.load(payload), "rrset_type", ("A", "AAAA", "CNAME")
                )
            )
            self.assertEqual(len(filtered), 6)


class TestUpdater(TestCase):
    def test_factory(self):
        conf = Config.factory("./tests/confs/two_domains.yaml")
        resolver = Locator("opendns")
        self.assertEqual(len(conf.dns_providers), 1)

        updaters = Updater.factory(conf, resolver)
        self.assertEqual(len(updaters), 2)

        self.assertEqual(updaters[0].domain, "somedomain.io")
        self.assertEqual(updaters[0].credentials, "some_key")
        self.assertEqual(updaters[0].subdomains, [("infra3", "AAAA"), ("infra", "A")])

        self.assertEqual(updaters[1].domain, "someotherdomain.io")
        self.assertEqual(updaters[1].credentials, "some_key")
        self.assertEqual(updaters[1].subdomains, [("blog", "A")])


class TestGandiUpdater(TestCase):
    """NB: intialize is not tested, for it would be a nightmare to patch / mock. This
    test class focuses rather on the different private methods involved in initialize"""

    def setUp(self):
        resolver = Locator("opendns")
        self.updater = GandiUpdater(
            "https://fake.gandi.net",
            "some_key",
            "somedomain.io",
            [("infra", "A"), ("infra3", "AAAA")],
            resolver,
        )

    @patch("dyndns_updater.updater.requests.get")
    def test_record_retreival(self, mock_get):
        with open("./tests/out/gandi_records_response.json") as payload_record:

            # mocking
            mock_get.return_value = Mock(ok=True)
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = json.load(payload_record)

            self.updater._get_records()

            self.assertEqual(len(self.updater.records), 2)
            self.assertEqual(self.updater.records[0].get("rrset_name"), "infra")
            self.assertEqual(
                self.updater.records[0].get("rrset_values"), ["148.86.98.105"]
            )
            # FIXME records should not include rrset_href
            self.assertEqual(
                self.updater.records[1],
                {
                    "rrset_href": "https://api.gandi.net/v5/livedns/domains/somedomain.io/records/infra3/AAAA",
                    "rrset_name": "infra3",
                    "rrset_ttl": 1800,
                    "rrset_type": "AAAA",
                    "rrset_values": ["a9f2:e357:31db:2a01:e0a:18d:c0:f416"],
                },
            )

    @patch("dyndns_updater.updater.requests.post")
    def test__record_missing(self, mock_post):
        # Initialization

        self.updater.records = [
            {
                "rrset_name": "infra3",
                "rrset_ttl": 1800,
                "rrset_type": "AAAA",
                "rrset_values": ["a9f2:e357:31db:2a01:e0a:18d:c0:f416"],
            }
        ]

        # mocking
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"message": "DNS Records Created"}
        self.updater.locator._query_dns_server = MagicMock(return_value="10.10.10.10")

        # testing
        self.updater._record_missing()

        # outgoing request
        mock_post.assert_called_with(
            "https://fake.gandi.net/domains/somedomain.io/records",
            headers={"Authorization": "Apikey some_key"},
            json={
                "rrset_type": "A",
                "rrset_name": "infra",
                "rrset_values": ["10.10.10.10"],
                "rrset_ttl": 1800,
            },
        )

        self.assertEqual(
            self.updater.records[1],
            {
                "rrset_name": "infra",
                "rrset_ttl": 1800,
                "rrset_type": "A",
                "rrset_values": ["10.10.10.10"],
            },
        )

    @patch("dyndns_updater.updater.requests.put")
    def test_updater(self, mock_put):
        # Initialization

        self.updater.records = [
            {
                "rrset_type": "A",
                "rrset_ttl": 1800,
                "rrset_name": "infra",
                "rrset_values": ["148.86.98.105"],
            },
            {
                "rrset_type": "AAAA",
                "rrset_ttl": 1800,
                "rrset_name": "infra3",
                "rrset_values": ["a9f2:e357:31db:2a01:e0a:18d:c0:f416"],
            },
        ]

        # Mock
        def _side_effect_func(value):
            if value == "4":
                return "10.10.10.10"
            elif value == "6":
                return "d6e0:11ea:f0ed:2a01:e0a:18d:c0:3192"

        self.updater.locator._query_dns_server = MagicMock(
            side_effect=_side_effect_func
        )
        mock_put.return_value = Mock(ok=True)
        mock_put.return_value.status_code = 201
        mock_put.return_value.json.return_value = {"message": "DNS Record Created"}

        self.updater.check_and_update()

        # Records get updated for future comparitions
        self.assertEqual(
            self.updater.records,
            [
                {
                    "rrset_type": "A",
                    "rrset_ttl": 1800,
                    "rrset_name": "infra",
                    "rrset_values": ["10.10.10.10"],
                },
                {
                    "rrset_type": "AAAA",
                    "rrset_ttl": 1800,
                    "rrset_name": "infra3",
                    "rrset_values": ["d6e0:11ea:f0ed:2a01:e0a:18d:c0:3192"],
                },
            ],
        )


class TestLocator(TestCase):
    def test_wrapping(self):
        resolver = Locator("opendns")
        self.assertEqual(resolver.dns_service["rdclass"], "IN")
        self.assertEqual(resolver._query, "myip.opendns.com")

    def test_using_unknown_dns_service_raises_exception(self):
        with pytest.raises(NotImplementedError):
            Locator("unknown service")

    def test_ip_string_format(self):
        resolver = Locator("opendns")
        current_ip = resolver.local_ipv4

        self.assertEqual(type(current_ip), str)

        self.assertTrue(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", current_ip))
