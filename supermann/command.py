from __future__ import absolute_import, unicode_literals

import argparse
import shlex

import supermann.core
import supermann.memmon
import supermann.metrics
import supermann.metrics.system
import supermann.metrics.process
import supermann.signals


def CustomHelpFormatter(*args, **kwargs):
    """Builds a modified argparse formatter"""
    kwargs.setdefault('max_help_position', 32)
    kwargs.setdefault('width', 96)
    return argparse.HelpFormatter(*args, **kwargs)


class ShlexArgumentParser(argparse.ArgumentParser):
    """Reads argument files using shlex"""

    def __init__(self, **kwargs):
        kwargs.setdefault('fromfile_prefix_chars', '@')
        super(ShlexArgumentParser, self).__init__(**kwargs)

    def convert_arg_line_to_args(self, line):
        for arg in shlex.split(line):
            yield arg


parser = ShlexArgumentParser(formatter_class=CustomHelpFormatter)
parser.add_argument(
    '-v', '--version', action='version',
    version='Supermann v{version} by {author}'.format(
        version=supermann.__version__,
        author=supermann.__author__),
    help="Show this programs version and exit")
parser.add_argument(
    '-l', '--log-level', metavar='LEVEL',
    default='INFO', choices=supermann.utils.LOG_LEVELS.keys(),
    help="One of CRITICAL, ERROR, WARNING, INFO, DEBUG")
parser.add_argument(
    'host', type=str, nargs='?', default='localhost',
    help="The Riemann server to connect to")
parser.add_argument(
    'port', type=int, nargs='?', default=5555,
    help="The Riemann server to connect to")
parser.add_argument(
    '-m', '--memmon', metavar='process=limit', action='append', default=[],
    help="A memory limit for a process")


def main():
    args = parser.parse_args()

    # Log messages are sent to stderr, and Supervisor takes care of the rest
    supermann.utils.configure_logging(args.log_level)

    # Create a Supermann instance
    self = supermann.core.Supermann(host=args.host, port=args.port)

    # Collect system metrics when an event is received
    self.connect(supermann.signals.event, supermann.metrics.system.cpu)
    self.connect(supermann.signals.event, supermann.metrics.system.mem)
    self.connect(supermann.signals.event, supermann.metrics.system.swap)
    self.connect(supermann.signals.event, supermann.metrics.system.load)

    # Collect metrics for each process when an event is recived
    self.connect(supermann.signals.process, supermann.metrics.process.cpu)
    self.connect(supermann.signals.process, supermann.metrics.process.mem)
    self.connect(supermann.signals.process, supermann.metrics.process.fds)
    self.connect(supermann.signals.process, supermann.metrics.process.state)
    self.connect(supermann.signals.process, supermann.metrics.process.uptime)

    # Monitor process memory
    if args.memmon:
        memmon = supermann.memmon.MemoryMonitor.from_args(*args.memmon)
        self.connect(supermann.signals.process, memmon.process)

    # Supermann will attempt to run forever
    self.run()
