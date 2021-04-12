from dyndns_updater import __version__
from unittest import TestCase
from dyndns_updater.updater import GandiUpdater, Updater
from unittest.mock import Mock, patch

class GandiUpdater(TestCase): 

    # FIXME: error occurs with this constructor only during pytest
    @patch('dyndns_updater.updater.requests.post')
    def test_constructor_inheritance(self, mock_get): 
        updater = GandiUpdater('https://dns.api.gandi.net/api/v5','some_key', 'somedomain.io', ['tower'])
