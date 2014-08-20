"""Blinker signals used for sending end receiving events"""

from __future__ import absolute_import, unicode_literals

import blinker

namespace = blinker.Namespace()

#: The event signal is sent when Supermann receives an event from Supervisor
#: Receivers should take `sender` (the Supermann instance) and `event` as args
event = namespace.signal('supervisor:event')

#: The process signal is sent for each Supervisor child process when an event
#: is received. It is sent a ``psutil.Process`` object for that process, and
#: the data from the Supervisor ``getProcessInfo`` function.
process = namespace.signal('supervisor:process')
