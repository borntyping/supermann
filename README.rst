=========
Supermann
=========

.. image:: http://img.shields.io/pypi/v/supermann.svg
    :target: https://pypi.python.org/pypi/supermann

.. image:: http://img.shields.io/pypi/l/supermann.svg
    :target: https://pypi.python.org/pypi/supermann

.. image:: http://img.shields.io/travis/borntyping/supermann/master.svg
    :target: https://travis-ci.org/borntyping/supermann

|

Supermann monitors processes running under `Supervisor <http://supervisord.org/>`_ and sends metrics to `Riemann <http://riemann.io/>`_.

* `Source on GitHub <https://github.com/borntyping/supermann>`_
* `Documentation on Read the Docs <http://supermann.readthedocs.org/en/latest/>`_
* `Packages on PyPI <https://pypi.python.org/pypi/supermann>`_

Usage
-----

Supermann runs as a Supervisor event listener, and will send metrics every time an event is received. The only configuration Supermann needs is the host and port for a Riemann instance, which can be provided as arguments or by the ``RIEMANN_HOST`` and ``RIEMANN_PORT`` environment variables.

Basic usage is as follows, though Supermann will not start if not run under Supervisor::

    supermann [--log-level=LEVEL] HOST PORT

A Supervisor configuration file for Supermann should look something like this::

    [eventlistener:supermann]
    command=supermann-from-file /etc/supermann.args
    events=PROCESS_STATE,TICK_5

This loads Supermann's arguments from ``/etc/supermann.args``, which would contain a host and port for a Riemann server - ``localhost:5555`` is used as the default if no host or port are specified::

    riemann.example.com 5555

What Supermann does
^^^^^^^^^^^^^^^^^^^

Supermann will collect and send information about the system and the processes running under Supervisor each time an event is received. Listening for the ``TICK_5`` and ``PROCESS_STATE`` events will collect and send information every 5 seconds, and when a program changes state. See the `Supervisor event documentation <http://supervisord.org/events.html>`_ for more information.

Supermann is designed to bail out when an error is encountered, allowing Supervisor to restart it - it is recommended that you do not set ``autorestart=false`` in the Supervisor configuration for the event listener. Logs are sent to ``STDERR`` for collection by Supervisor - the log level can be controlled with the ``--log-level`` argument. The logs can be read with ``supervisorctl tail supermann stderr`` or finding the log in Supervisor's log directory.

``supermann-from-file``
^^^^^^^^^^^^^^^^^^^^^^^

An issue with modifying the configuration of a Supervisord event listener (`link <https://github.com/Supervisor/supervisor/issues/339>`_) means that the command used to start an event listener process can't be changed while Supervisord is running.

Supermann 2 allowed files to be named directly as an argument that more arguments would be read from. Supermann 3 instead provides the ``supermann-from-file`` entry point, which loads a file containing arguments that will be passed to the main ``supermann`` command.

The easiest way to upgrade between versions is to rename the ``eventlistener:supermann`` section in the Supervisord configuration, and to then run ``supervisorctl update``. This will remove the old supermann instance, and start a new instance with the new command. The ``supermann-from-file`` command reads a set of arguments from a file and starts Supermann with those arguments, so that Supermann's configuration can be changed without restarting Supervisord.

Installation
------------

Supermann can be installed with ``pip install supermann``. It's recommended to install it in the same Python environment as Supervisor.

Supervisor can also be installed with ``pip``, or can be installed from your distributions package manager. Once Supermann is installed, add an ``eventlistener`` section to the Supervisor configuration (``/etc/supervisord.conf`` by default) and restart Supervisor.

Requirements
^^^^^^^^^^^^

* `click <http://click.pocoo.org/>`_
* `blinker <https://pythonhosted.org/blinker/>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_
* `psutil <http://pythonhosted.org/psutil/>`_
* `riemann-client <http://riemann-client.readthedocs.org/>`_
* `supervisor <http://supervisord.org/>`_

The ``psutil`` package uses C extensions, and installing the package from source or with a python package manager (such as ``pip``) will require build tools. Alternatively, it can be installed from your distribution's repositories (``python-psutil`` on Debian and CentOS). Superman currently uses a very old version of ``psutil`` so as to remain compatible with CentOS.

Supermann is developed and tested on Python 2.6. There are no plans to release it for Python 3, as Google's ``protobuf`` library (and therefore ``riemann-client``) are only compatible with Python 2.

Changelog
---------

Version 3.0.0
^^^^^^^^^^^^^

* Upgraded to most recent version of ``psutil`` (``2.1.1``)
* Replaced or changed various metrics
* Replaced ``argparse`` with ``click`` and made improvements to CLI
* Replaced ``@file`` argument syntax with ``supermann-from-file``
* Removed ``--memmon`` option and memory monitoring plugin
* Added documentation on `Read the Docs <http://supermann.readthedocs.org/en/latest/>`_
* Many other minor fixes and improvements

Licence
-------

Supermann is licensed under the `MIT Licence <http://opensource.org/licenses/MIT>`_. The protocol buffer definition is sourced from the `Riemann Java client <https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto>`_, which is licensed under the `Apache Licence <http://www.apache.org/licenses/LICENSE-2.0>`_.

Authors
-------

Supermann was written by `Sam Clements <https://github.com/borntyping>`_, while working at `DataSift <https://datasift.com>`_.

.. image:: https://0.gravatar.com/avatar/8dd5661684a7385fe723b7e7588e91ee?d=https%3A%2F%2Fidenticons.github.com%2Fe83ef7586374403a328e175927b98cac.png&r=x&s=40
.. image:: https://1.gravatar.com/avatar/a3a6d949b43b6b880ffb3e277a65f49d?d=https%3A%2F%2Fidenticons.github.com%2F065affbc170e2511eeacb3bd0e975ec1.png&r=x&s=40
