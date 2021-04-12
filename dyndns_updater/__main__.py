import argparse

parser = argparse.ArgumentParser()

parser.add_argument("mode", choices=('now','scheduled'), help="'now' (instantaneous one shot update) OR 'scheduled' (dyndns_updater will perform the update)")

args = parser.parse_args()

print(args.mode)