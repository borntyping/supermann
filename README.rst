=========
Supermann
=========

A `Supervisor`_ event listener for `Riemann`_.

Requirements
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_
* `protobuf <https://pypi.python.org/pypi/protobuf>`_
* `psutil <https://pypi.python.org/pypi/psutil>`_

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
    command=supermann
    events=PROCESS_STATE,TICK_5
    autorestart=true

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

Supermann is licensed under the `MIT Licence`_.

The protocol buffer definition is sourced from the `Riemann Java client`_,
which is licensed under the `Apache Licence`_.

Authors
-------

Supermann was written by `Sam Clements`_, while working at `DataSift`_.

.. _Supervisor: http://supervisord.org/
.. _Riemann: http://riemann.io/
.. _Riemann Java client: https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto
.. _MIT Licence: http://opensource.org/licenses/MIT
.. _Apache Licence: http://www.apache.org/licenses/LICENSE-2.0
.. _Sam Clements: https://github.com/borntyping
.. _DataSift: https://datasift.com
