# dynDNS_updater
standalone DNS updater for Gandi

The main purpose of **dynDNS_updater** is to keep the DNS records pointing to your servers up to date **without any system dependencies** (except python, of course) nor any fancy web services to identify their public IPv4 / IPv6

## Usage

```yaml
ip_identifier: cloudflare
delta : 900
dns_providers: 
  - gandi: GKDNzPZsdHB8vxA56voERCiC
    somedomain.io:
      tower: A
      tower6: AAAA
      tower2: AAAA
```

## Features

Types of records

* A
* AAAA

### Supported DNS provider

|      Name | API root                         |
| --------: | :------------------------------- |
| **Gandi** | https://api.gandi.net/v5/livedns |

## Developpers 

### Onboarding

* [poetry]()
* []()

```bash
git clone https://github.com/zar3bski/dynDNS_updater.git
cd dynDNS_updater
poetry install 
```
