=========
Supermann
=========

.. image:: https://pypip.in/v/supermann/badge.png
    :target: https://pypi.python.org/pypi/supermann

.. image:: https://travis-ci.org/borntyping/supermann.png?branch=master
    :target: https://travis-ci.org/borntyping/supermann

Supermann monitors processes running under `Supervisor <http://supervisord.org/>`_ and sends metrics to `Riemann <http://riemann.io/>`_.

Requirements
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_
* `psutil <https://pypi.python.org/pypi/psutil>`_
* `supervisor <https://pypi.python.org/pypi/supervisor>`_

The psutil package uses C extensions, and installing the package from source or
with a python package manager (such as ``pip``) will require build tools.
Alternatively, it can be installed from your distribution's repositories
(``python-psutil`` on Debian and CentOS).

Supermann is developed and tested on Python 2.6. There are no plans to release
it for Python 3, as Google's ``protobuf`` library is only compatible with
Python 2. However, the code is written to run on Python 2.6, 2.7 and 3.

Configuration
-------------

Supermann runs as a Supervisor event listener::

    [eventlistener:supermann]
    command=supermann localhost 5555
    events=PROCESS_STATE,TICK_5
    autorestart=true

Run `supermann --help` for usage information.

Notes
-----

The Protocol buffer definition can be rebuilt using the most recent version::

    wget https://github.com/aphyr/riemann-java-client/blob/master/src/main/proto/riemann/proto.proto
    protoc --python_out=supermann/riemann/ riemann.proto

If supermann is used as a library, you will need to ensure that the log messages
Supermann emits are handled. This can be done by either configuring the python
logging module, calling ``supermann.command.configure_logging``, or adding a
null handler::

    import logging

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    logging.getLogger('supermann').addHandler(NullHandler())

Supermann should never send events with a nil host, and will always use the current hostname as the default host for events.

Licence
-------

Supermann is licensed under the `MIT Licence <http://opensource.org/licenses/MIT>`_. The protocol buffer definition is sourced from the `Riemann Java client <https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto>`_,
which is licensed under the `Apache Licence <http://www.apache.org/licenses/LICENSE-2.0>`_.

Authors
-------

Supermann was written by `Sam Clements <https://github.com/borntyping>`_, while working at `DataSift <https://datasift.com>`_.

.. image:: https://0.gravatar.com/avatar/8dd5661684a7385fe723b7e7588e91ee?d=https%3A%2F%2Fidenticons.github.com%2Fe83ef7586374403a328e175927b98cac.png&r=x&s=40
.. image:: https://1.gravatar.com/avatar/a3a6d949b43b6b880ffb3e277a65f49d?d=https%3A%2F%2Fidenticons.github.com%2F065affbc170e2511eeacb3bd0e975ec1.png&r=x&s=40
