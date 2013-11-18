from __future__ import absolute_import, unicode_literals

import argparse
import logging

from supermann import Supermann

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s (%(name)s)'

LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def configure_logging(level=logging.INFO):
    if isinstance(level, basestring):
        level = LOG_LEVELS.get(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log = logging.getLogger('supermann')
    log.setLevel(level)
    log.addHandler(handler)


def formatter_class(*args, **kwargs):
    kwargs.setdefault('max_help_position', 32)
    return argparse.ArgumentDefaultsHelpFormatter(*args, **kwargs)


parser = argparse.ArgumentParser(formatter_class=formatter_class)
parser.add_argument(
    '-l', '--log-level', metavar='LEVEL',
    default='INFO', choices=LOG_LEVELS.keys(),
    help="One of CRITICAL, ERROR, WARNING, INFO, DEBUG")


def main():
    args = parser.parse_args()

    configure_logging(args.log_level)

    supermann = Supermann()
    supermann.check_parent()
    supermann.run()
