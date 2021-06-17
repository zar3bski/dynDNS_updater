import argparse
import schedule
import logging
from dyndns_updater.utils import Config
from dyndns_updater.updater import Updater
from dyndns_updater.locator import Locator


def main():
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
    locator = Locator(config.ip_identifier)
    updaters = Updater.factory(config, locator)

    list(map(lambda x: x.initialize(), updaters))

    if args.mode == "now":
        list(map(lambda x: x.check_and_update(), updaters))
    elif args.mode == "scheduled":
        schedule.every(config.delta).seconds.do(
            list(map(lambda x: x.check_and_update(), updaters))
        )
        while True:
            schedule.run_pending()

    logging.info("dyndns_updater exited normally")


if __name__ == "__main__":
    main()
