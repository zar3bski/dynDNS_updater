from dyndns_updater import __version__
from unittest import TestCase
from dyndns_updater.updater import GandiUpdater, Updater
from unittest.mock import Mock, patch

class TestGandiUpdater(TestCase): 

    @patch('dyndns_updater.updater.requests.post')
    def test_constructor_inheritance(self, mock_get): 

        normal_response = {"message": "Zone Created", "uuid": "ee788920-9bc5-11eb-823b-00163ea99cff"}

        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = normal_response
        
        updater = GandiUpdater('https://dns.api.gandi.net','some_key', 'somedomain.io', ['tower'])
        self.assertEqual(updater.zone_uuid, "ee788920-9bc5-11eb-823b-00163ea99cff")
