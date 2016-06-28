"""Command line entry points to supermann using click"""

from __future__ import absolute_import, unicode_literals

import click

import supermann.core
import supermann.utils


@click.command()
@click.version_option(version=supermann.__version__)
@click.option(
    '-l', '--log-level', default='INFO',
    type=click.Choice(supermann.utils.LOG_LEVELS.keys()),
    help="One of CRITICAL, ERROR, WARNING, INFO, DEBUG.")
@click.option(
    '-s', '--system', type=click.BOOL, default=True,
    help='Enable or disable system metrics.')
@click.argument(
    'host', type=click.STRING, default='localhost', envvar='RIEMANN_HOST')
@click.argument(
    'port', type=click.INT, default=5555, envvar='RIEMANN_PORT')
def main(log_level, host, port, system):
    """The main entry point for Supermann"""
    # Log messages are sent to stderr, and Supervisor takes care of the rest
    supermann.utils.configure_logging(log_level)

    s = supermann.core.Supermann(host, port)
    if system:
        s.connect_system_metrics()
    s.connect_process_metrics()
    s.run()


@click.command()
@click.argument('config', type=click.File('r'))
def from_file(config):
    """An alternate entry point that reads arguments from a file."""
    main.main(args=config.read().split())
