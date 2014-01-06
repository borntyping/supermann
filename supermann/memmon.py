"""A memory monitoring module for Supermann"""

from __future__ import absolute_import, unicode_literals

import supermann.utils


class MemoryMonitor(object):
    @classmethod
    def from_args(cls, process_list):
        processes = dict()
        for process in process_list:
            name, limit = process.split('=')
            processes[name] = int(limit)
        return cls(processes)

    def __init__(self, processes=None):
        self.processes = processes or dict()
        self.log = supermann.utils.getLogger(self)
        self.log.info("Memory monitoring processes: {0}".format(
            ', '.join(self.processes.keys())))

    def process(self, sender, process, name, **data):
        """Recives supermann.signals.process"""
        if process and name in self.processes:
            limit = self.processes[name]
            rss, vms = process.get_memory_info()
            if rss > limit:
                self.restart_process(sender, name)

    def restart_process(self, sender, name):
        self.log.info("Restarting process {0}".format(name))
        self.log.debug("Stopping process {0}".format(name))
        sender.supervisor.rpc.stopProcess(name)
        self.log.debug("Starting process {0}".format(name))
        sender.supervisor.rpc.startProcess(name, wait=False)
