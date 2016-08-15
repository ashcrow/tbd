# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Investigator plugin which allows control of investigators via the wsbus.
"""

import os

from cherrypy.process import plugins

from multiprocessing import Process, Queue
from commissaire.jobs.investigator import investigator


class InvestigatorPlugin(plugins.SimplePlugin):

    def __init__(self, bus):
        """
        Creates a new instance of the InvestigatorPlugin.

        :param bus: The CherryPy bus.
        :type bus: cherrypy.process.wspbus.Bus
        """
        plugins.SimplePlugin.__init__(self, bus)
        # multiprocessing.Process() uses fork() to execute the target
        # function.  That means the child process inherits the entire
        # state of the main process, this plugin included.
        #
        # When this process is forked, self.process will be a valid
        # Process object but self.process in the child process will
        # not.  We capture our own PID up front so the we can later
        # distinguish whether we're the parent or child process and
        # avoid interacting with an invalid Process object.
        self.main_pid = os.getpid()
        self.request_queue = Queue()
        self.process = Process(
            target=investigator,
            args=(self.request_queue,))

    def start(self):
        """
        Starts the plugin and the investigator process.
        """
        self.bus.log('Starting up Investigator plugin')
        self.bus.subscribe('investigator-is-alive', self.is_alive)
        self.bus.subscribe('investigator-submit', self.submit)
        self.process.start()

    def stop(self):
        """
        Stops the plugin.
        """
        self.bus.log('Stopping down Investigator plugin')
        self.bus.unsubscribe('investigator-is-alive', self.is_alive)
        self.bus.unsubscribe('investigator-submit', self.submit)
        if os.getpid() == self.main_pid:
            self.process.terminate()
            self.process.join()

    def submit(self, store_manager, host):
        """
        Submits a new request to the investigator process.

        :param store_manager: A store manager (will be cloned)
        :type store_manager: commissaire.store.storehandlermanager.
                             StoreHandlerManager
        :param host: A Host model representing the host to investigate.
        :type host: commissaire.handlers.models.Host
        """
        manager_clone = store_manager.clone()
        job_request = (manager_clone, host.__dict__)
        self.request_queue.put(job_request)

    def is_alive(self):
        """
        Returns whether the investigator process object is alive.

        The investigator process object is alive from the moment the
        start() method returns until the child process terminates.

        :returns: Whether the investigator is alive
        :rtype: bool
        """
        return self.process.is_alive()


#: Generic name for the plugin
Plugin = InvestigatorPlugin
