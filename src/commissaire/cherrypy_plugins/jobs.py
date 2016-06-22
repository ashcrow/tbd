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
Plugin to allow submission of remote jobs to a thread pool.
"""

from cherrypy.process import plugins

# XXX This is a poor man's thread pool, but it's the only one available
#     in Python 2's standard library.  There are 3rd party modules that
#     might work better.  Also Python 3.2 introduced concurrent.futures.
from multiprocessing.pool import ThreadPool


class JobsPlugin(plugins.SimplePlugin):

    def __init__(self, bus):
        """
        Creates a new instance of the JobsPlugin.

        :param bus: The CherryPy bus.
        :type bus: cherrypy.process.wspbus.Bus
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.pool = None

    def start(self):
        """
        Starts the plugin and the thread pool.
        """
        self.bus.log('Starting up Jobs plugin')
        self.pool = ThreadPool()
        self.bus.subscribe('submit-job', self.submit_job)

    def stop(self):
        """
        Stops the plugin.
        """
        self.bus.log('Stopping down Jobs plugin')
        self.bus.unsubscribe('submit-job', self.submit_job)
        self.pool.close()
        # XXX Don't call pool.join().  The ThreadPool tries to
        #     join with the current thread, which is an error.
        #     Guessing that's due to lack of testing since it
        #     thinks it's a process pool and the ThreadPool
        #     class is kind of an Easter Egg in the library.

    def submit_job(self, func, args=(), kwds={}, callback=None):
        """
        Submits a job to the thread pool.

        :param func: The callable to invoke in a thread.
        :type func: callable
        :param args: Optional argument tuple.
        :type args: tuple
        :param kwds: Optional keyword arguments.
        :type kwds: dict
        :param callback: Optional callable to invoke when the job is complete.
                         The callable takes a multiprocessing.pool.AsyncResult
                         argument.
        :type callback: callable
        """
        name = getattr(func, '__name__', repr(func))
        self.bus.log('Job submission: {0}'.format(name))
        self.pool.apply_async(func, args, kwds, callback)


#: Generic name for the plugin
Plugin = JobsPlugin
