"""The Supermann core"""

from __future__ import absolute_import, unicode_literals

import blinker

namespace = blinker.Namespace()

# The event signal is sent each time Supermann recives an event from Supervisor
# Recivers should take `sender` (the Supermann instance) and `event` as args
event = namespace.signal('supervisor:event')

# The process signal is sent for each Supervisor child process when an event
# is recived. It is sent a psutil.Process object for that process, and the data
# from the Supervisor getProcessInfo function.
#
# http://supervisord.org/api.html
# supervisor.rpcinterface.SupervisorNamespaceRPCInterface.getProcessInfo
process = namespace.signal('supervisor:process')
