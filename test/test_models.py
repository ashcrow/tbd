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
Unittests for the main models module.
"""

from mock import MagicMock

from . import TestCase, TestingObj

from commissaire import models


class Test_Server(TestCase):
    """
    Tests for _Server
    """

    def before(self):
        """
        Called before every test.
        """
        self.client = MagicMock()
        self.client.get.return_value = True
        self.client.write.return_value = True
        self.client.delete.return_value = True

        self.testing_obj = TestingObj(anint=10)

    def after(self):
        """
        Called after every test.
        """
        self.client = None

    def test_creation_and_verify_client(self):
        """
        Verify _verify_client works as expected.
        """
        # Validate the client must have the proper methods
        self.assertRaises(ValueError, models._Server, dict())

        # No error when the proper methods are available
        server = models._Server(self.client)
        self.assertEquals(self.client, server.client)

    def test_save(self):
        """
        Verify save works as expected.
        """
        server = models._Server(self.client)
        server.save(self.testing_obj)
        # We should have one write
        self.client.write.assert_called_once_with(
            '/testing/anint', 10, quorum=True)

    def test_read(self):
        """
        Verify read works as expected.
        """
        server = models._Server(self.client)
        self.client.read.return_value = MagicMock(value="10")

        # Create the object with different data
        to = server.read(TestingObj(anint=1))
        # We should have one read
        self.client.read.assert_called_once_with(
            '/testing/anint', quorum=True)
        # And it should have set the data to 10
        self.assertEquals(10, to.anint)
