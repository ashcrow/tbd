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
Test cases for the commissaire.cherrypy_plugins.jobs module.
"""

import mock
import multiprocessing

from . import TestCase
from commissaire.cherrypy_plugins.jobs import Plugin


class Test_JobsPlugin(TestCase):
    """
    Tests for the JobsPlugin class.
    """

    #: Topics that should be registered
    topics = ('submit-job', )

    def before(self):
        """
        Called before every test.
        """
        self.bus = mock.MagicMock()
        self.plugin = Plugin(self.bus)

    def after(self):
        """
        Called after every test.
        """
        self.bus = None
        self.plugin = None

    def test_jobs_plugin_creation(self):
        """
        Verify that the creation of the plugin works as it should.
        """
        # Thread pool should not be created until start()
        self.assertIsNone(self.plugin.pool)

    def test_jobs_plugin_start(self):
        """
        Verify start() starts the background process.
        """
        self.plugin.start()

        self.assertIsNotNone(self.plugin.pool)

        # Number of worker threads currently matches CPU count
        # (this will very likely change, but it's a start point)
        cpu_count = multiprocessing.cpu_count()
        self.assertEqual(self.plugin.pool._processes, cpu_count)

        # There should be bus subscribed topics
        for topic in self.topics:
            self.bus.subscribe.assert_any_call(topic, mock.ANY)

        self.plugin.stop()

    def test_jobs_plugin_stop(self):
        """
        Verify stop() unsubscribes topics.
        """
        self.plugin.start()
        self.plugin.stop()

        # Thread pool is not destroyed immediately
        self.assertIsNotNone(self.plugin.pool)

        # unsubscribe should be called a specific number of times
        self.assertEquals(len(self.topics), self.bus.unsubscribe.call_count)

        # Each unsubscription should have it's own call
        # to deregister a callback
        for topic in self.topics:
            self.bus.unsubscribe.assert_any_call(topic, mock.ANY)
