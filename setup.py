#!/usr/bin/env python2.6

from __future__ import unicode_literals

import setuptools
import sys

setuptools.setup(
    name = "supermann",
    version = '1.8.0',

    author = "Sam Clements",
    author_email = "sam.clements@datasift.com",

    url = "https://github.com/borntyping/supermann",
    description = "A Supervisor event listener for Riemann",
    long_description = open('README.rst').read(),

    packages = setuptools.find_packages(),

    install_requires = [
        'argparse==1.1',
        'blinker==1.3',
        'protobuf==2.5.0',
        'psutil==1.2.0',
        'riemann-client==3.0.1',
        'supervisor==3.0',
    ],

    entry_points = {
        'console_scripts': [
            'supermann = supermann.command:main',
            'supermann-{0}.{1} = supermann.command:main'.format(*sys.version_info)
        ]
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: No Input/Output (Daemon)',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ],
)
