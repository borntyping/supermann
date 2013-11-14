=========
Supermann
=========

A `Supervisor`_ event listener for `Riemann`_.

Notes
-----

Supermann is developed and tested on Python 2.6 for CentOS 5 and 6. Tests are
run against Python 2.6 and 2.7, and while Google's ``protobuf`` library is not
compatible with Python 3, the package should should be compatible with Python 3.

The protocol buffer definition is sourced from the `Riemann Java client`_. It
can be rebuilt using the most recent definition with::

    wget https://github.com/aphyr/riemann-java-client/blob/master/src/main/proto/riemann/proto.proto
    protoc --python_out=supermann/riemann/ riemann.proto

Licence
-------

Supermann is licensed under the `MIT Licence`_.

Authors
-------

Supermann was written by `Sam Clements`_, while working at `DataSift`_.

.. _Supervisor: http://supervisord.org/
.. _Riemann: http://riemann.io/
.. _Riemann Java client: https://github.com/aphyr/riemann-java-client/blob/0c4a1a255be6f33069d7bb24d0cc7efb71bf4bc8/src/main/proto/riemann/proto.proto
.. _MIT Licence: http://opensource.org/licenses/MIT
.. _Sam Clements: https://github.com/borntyping
.. _DataSift: https://datasift.com
