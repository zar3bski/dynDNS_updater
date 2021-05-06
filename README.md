# dynDNS_updater
standalone DNS updater for Gandi


The main purpose of **dynDNS_updater** is to keep the DNS records pointing to your servers up to date **without any system dependencies** (except python, of course) nor any fancy web services to identify their public IPv4 / IPv6

## Usage

### Install

```bash
pip install dyndns-updater
```

### CLI

```
python -m  dyndns_updater {now,scheduled} /path/to/your/conf.yaml
```
Mode: 

* **now**: perform action once
* **scheduled**: perform action every `${delta}` seconds (see below)


### Configuration

```yaml
ip_identifier: cloudflare
delta : 900
dns_providers: 
  - gandi: GKDNzPZsdHB8vxA56voERCiC
    somedomain.io:
      subdomain1: A
      subdomain2: AAAA
      subdomain3: AAAA
```

|    variables    | description                                                                                        |
| :-------------: | :------------------------------------------------------------------------------------------------- |
| `ip_identifier` | DNS server used to determine your current IP (currently supporting **cloudflare** and **opendns**) |
|     `delta`     | How often should dynDNS_updater check and update (in seconds)                                      |
| `dns_providers` | list of `provider: API-KEY`                                                                        |


## Features

Types of records

* A
* AAAA

### Supported DNS provider

|      Name | API root                         |
| --------: | :------------------------------- |
| **Gandi** | https://api.gandi.net/v5/livedns |

## Developpers 

If your favorite DNS provider is missing from the list, please consider contributing. Your class just needs to inherit from `Updater` and possess the following methods to work in dynDNS_updater

```python
class YourProviderUpdater(Updater):
    def initialize(self):
        your_logic = "please write unit tests along the way"

    def check_and_update(self):
        your_logic = "please write unit tests along the way"
```

### Onboarding

* [poetry](https://python-poetry.org/): dependency manager
* [black](https://black.readthedocs.io/en/stable/): code formater

```bash
git clone https://github.com/zar3bski/dynDNS_updater.git
cd dynDNS_updater
poetry install 
```

This will create a virtual env with all dev dependencies

#### Some usefull commands

* run **unit tests** : `poetry run pytest`
* add dependencies : `poetry add some-lib`


