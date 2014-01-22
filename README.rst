=========
Supermann
=========

.. image:: https://pypip.in/v/supermann/badge.png
    :target: https://pypi.python.org/pypi/supermann

.. image:: https://travis-ci.org/borntyping/supermann.png?branch=master
    :target: https://travis-ci.org/borntyping/supermann

Supermann monitors processes running under `Supervisor <http://supervisord.org/>`_ and sends metrics to `Riemann <http://riemann.io/>`_.

Usage
-----

Supermann runs as a Supervisor event listener, and will send metrics every time an event is received.

A very basic Supervisor configuration section to run Supermann::

    [eventlistener:supermann]
    command=supermann localhost 5555
    events=PROCESS_STATE,TICK_5

Listening for the ``PROCESS_STATE`` and ``TICK_5`` events will send metrics every 5 seconds, and when a program changes state. See the `Supervisor event documentation <http://supervisord.org/events.html>`_ for more information. Supermann is designed to bail out when an error is encountered, allowing Supervisor to restart it - it is recommended that you do not set ``autorestart=false`` in the Supervisor configuration for the eventlistener. Supervisor logs to ``stderr``, which is logged by Supervisor. The logs can be read with ``supervisorctl tail supermann stderr`` or finding the log in Supervisor's log directory.

``supermann --help`` will display usage information on the available arguments. Basic usage is::

    supermann [--log-level=INFO] [--memmon <name>=<limit>] $RIEMANN_HOST $RIEMANN_PORT

The ``--memmon`` option takes the name of a Supervisor program, and a memory limit in bytes. The suffixes ``gb``, ``mb`` and ``kb`` can be used, and are case insensitive. This option can be repeated any number of times.

Installation
------------

Supermann can be installed with ``pip install supermann``. Supervisor can also be installed with ``pip``, or can be installed from your distributions package manager. Once Supermann is installed, add an ``eventlistener`` section to the Supervisor configuration (``/etc/supervisord.conf`` by default) and restart Supervisor.

Requirements
^^^^^^^^^^^^

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_
* `psutil <https://pypi.python.org/pypi/psutil>`_
* `riemann-client <https://pypi.python.org/pypi/riemann-client>`_
* `supervisor <https://pypi.python.org/pypi/supervisor>`__

The psutil package uses C extensions, and installing the package from source or with a python package manager (such as ``pip``) will require build tools. Alternatively, it can be installed from your distribution's repositories (``python-psutil`` on Debian and CentOS).

Supermann is developed and tested on Python 2.6. There are no plans to release it for Python 3, as Google's ``protobuf`` library (and therefore ``riemann-client``) are only compatible with Python 2.

Licence
-------

Supermann is licensed under the `MIT Licence <http://opensource.org/licenses/MIT>`_. The protocol buffer definition is sourced from the `Riemann Java client <https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto>`_, which is licensed under the `Apache Licence <http://www.apache.org/licenses/LICENSE-2.0>`_.

Authors
-------

Supermann was written by `Sam Clements <https://github.com/borntyping>`_, while working at `DataSift <https://datasift.com>`_.

.. image:: https://0.gravatar.com/avatar/8dd5661684a7385fe723b7e7588e91ee?d=https%3A%2F%2Fidenticons.github.com%2Fe83ef7586374403a328e175927b98cac.png&r=x&s=40
.. image:: https://1.gravatar.com/avatar/a3a6d949b43b6b880ffb3e277a65f49d?d=https%3A%2F%2Fidenticons.github.com%2F065affbc170e2511eeacb3bd0e975ec1.png&r=x&s=40
