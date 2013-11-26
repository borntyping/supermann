from __future__ import absolute_import, unicode_literals

import argparse
import logging

import supermann.core
import supermann.metrics
import supermann.metrics.system
import supermann.metrics.process
import supermann.signals


LOG_FORMAT = '%(asctime)s %(levelname)-8s [%(name)s] %(message)s'

LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
}


def configure_logging(level=logging.INFO):
    """This configures the supermann log to output to the console"""
    if isinstance(level, basestring):
        level = LOG_LEVELS.get(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    log = logging.getLogger('supermann')
    log.setLevel(level)
    log.addHandler(handler)


def formatter_class(*args, **kwargs):
    """Builds a modified argparse formatter"""
    kwargs.setdefault('max_help_position', 32)
    return argparse.ArgumentDefaultsHelpFormatter(*args, **kwargs)


parser = argparse.ArgumentParser(formatter_class=formatter_class)
parser.add_argument(
    '-l', '--log-level', metavar='LEVEL',
    default='INFO', choices=LOG_LEVELS.keys(),
    help="One of CRITICAL, ERROR, WARNING, INFO, DEBUG")
parser.add_argument(
    'host', type=str, nargs='?', default='localhost',
    help="The Riemann server to connect to")
parser.add_argument(
    'port', type=int, nargs='?', default=5555,
    help="The Riemann server to connect to")


def main():
    args = parser.parse_args()

    # Log messages are sent to stderr, and Supervisor takes care of the rest
    configure_logging(args.log_level)

    # Create a Supermann instance, and check it is running under Supervisord
    self = supermann.core.Supermann(host=args.host, port=args.port)
    self.check_supervisor()

    # A tick signal should be emitted when Supervisord ticks
    self.connect(supermann.signals.event, supermann.metrics.system.cpu)
    self.connect(supermann.signals.event, supermann.metrics.system.mem)
    self.connect(supermann.signals.event, supermann.metrics.system.swap)

    # Supermann should emit a signal for each process being monitored
    self.connect(supermann.signals.process, supermann.metrics.process.cpu)
    self.connect(supermann.signals.process, supermann.metrics.process.mem)
    self.connect(supermann.signals.process, supermann.metrics.process.fds)
    self.connect(supermann.signals.process, supermann.metrics.process.state)

    # Supermann will then attempt to run forever
    self.run()
