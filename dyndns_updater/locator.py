from dns.resolver import Resolver
import logging
import argparse

logging.basicConfig(level=logging.INFO)


class Locator(Resolver):
    """A robust way to identify your public ipv4 / ipv6 without any system dependence
    usage:
        locator = Locator(provider) | supported providers are opendns and cloudflare
    """

    dns_servers = {
        "opendns": {
            "4": {"servers": ["208.67.222.222", "208.67.220.220"], "rdtype": "A"},
            "6": {"servers": ["2620:119:35::35", "2620:119:53::53"], "rdtype": "AAAA"},
            "query": "myip.opendns.com",
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
        if nameserver in Locator.dns_servers.keys():
            super().__init__(configure=False)
            self.dns_service = Locator.dns_servers[nameserver]
            self._query = Locator.dns_servers[nameserver]["query"]
            self._rdclass = Locator.dns_servers[nameserver]["rdclass"]
        else:
            raise NotImplementedError(
                "Locator isn't configured to work with {}. Valid options are {}".format(
                    nameserver, Locator.dns_servers.keys()
                )
            )

    def _query_dns_server(self, ip_version):
        self.nameservers = self.dns_service[ip_version]["servers"]
        answer = self.resolve(
            qname=self._query,
            rdtype=self.dns_service[ip_version]["rdtype"],
            rdclass=self._rdclass,
        )
        return answer.response.answer[0][0].to_text().strip('"')

    @property
    def local_ipv4(self):
        try:
            self._local_ipv4 = self._query_dns_server("4")
            return self._local_ipv4
        except:
            logging.warning(
                "Could not determin local IPv4 while querying {}: returning cached value ({})".format(
                    self._query, self._local_ipv4
                )
            )
            return self._local_ipv4

    @property
    def local_ipv6(self):
        try:
            self._local_ipv6 = self._query_dns_server("6")
            return self._local_ipv6
        except:
            logging.warning(
                "Could not determin local IPv6 while querying {}: returning cached value ({})".format(
                    self._query, self._local_ipv6
                )
            )
            return self._local_ipv6


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip_identifier", choices=Locator.dns_servers.keys())
    args = parser.parse_args()

    locator = Locator(args.ip_identifier)
    print("current IPv4: {}".format(locator.local_ipv4))
    print("current IPv6: {}".format(locator.local_ipv6))
