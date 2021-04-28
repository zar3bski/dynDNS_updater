import argparse
import schedule
import logging
from dyndns_updater.utils import Config
from dyndns_updater.updater import Updater
from dyndns_updater.locator import Locator

logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()

parser.add_argument(
    "mode",
    choices=("now", "scheduled"),
    help="'now' (instantaneous one shot update) OR 'scheduled' (dyndns_updater will perform the update)",
)
parser.add_argument("config_path", help="path to a valid conf file")

args = parser.parse_args()

config = Config.factory(args.config_path)
updaters = Updater.factory(config)
locator = Locator(config.ip_identifier)

map(lambda x: x.initialize(), updaters)
map(lambda x: x.record_missing(locator), updaters)

if args.mode == "now":
    map(lambda x: x.check_and_update(locator), updaters)
elif args.mode == "scheduled":
    schedule.every(config.delta).seconds.do(
        map(lambda x: x.check_and_update(locator), updaters)
    )
    while True:
        schedule.run_pending()
