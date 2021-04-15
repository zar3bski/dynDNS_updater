from dns.resolver import Resolver
import re


class Locator(Resolver):
    """A robust way to identify your public ipv4 / ipv6 without any system dependence
    usage:
        locator = Locator(provider) | supported providers are opendns, google and cloudflare
    """

    dns_servers = {
        "opendns": {
            "4": {"servers": ["208.67.222.222", "208.67.220.220"], "rdtype": "A"},
            "6": {"servers": ["2620:119:35::35", "2620:119:53::53"], "rdtype": "AAAA"},
            "query": "myip.opendns.com",
            "rdclass": "IN",
        },
        "google": {
            "4": {"servers": ["8.8.8.8", "8.8.4.4"], "rdtype": "TXT"},
            "6": {
                "servers": ["2001:4860:4860::8888", "2001:4860:4860::8844"],
                "rdtype": "TXT",
            },
            "query": "o-o.myaddr.l.google.com",
            "rdclass": "IN",
        },
        "cloudflare": {
            "4": {"servers": ["1.1.1.1", "1.0.0.1"], "rdtype": "TXT"},
            "6": {
                "servers": ["2606:4700:4700::1111", "2606:4700:4700::1001"],
                "rdtype": "TXT",
            },
            "query": "whoami.cloudflare",
            "rdclass": "CH",
        },
    }

    def __init__(self, nameserver):
        super(Locator, self).__init__(configure=False)
        self.dns_service = Locator.dns_servers[nameserver]
        self._query = Locator.dns_servers[nameserver]["query"]
        self._rdclass = Locator.dns_servers[nameserver]["rdclass"]

    def _query_dns_server(self, ip_version): 
        self.nameservers = self.dns_service[ip_version]["servers"]
        answer = self.resolve(
            qname=self._query,
            rdtype=self.dns_service[ip_version]["rdtype"],
            rdclass=self._rdclass,
        )
        return answer.response.answer[0]

    #TODO: find the proper way to store / cache and retreive it
    @property
    def local_ipv4(self):
        return self._query_dns_server("4")[0]

    @property
    def local_ipv6(self):
        return self._query_dns_server("6")[0]
        