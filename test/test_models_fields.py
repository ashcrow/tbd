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
Unittests for fields.
"""

import datetime

from . import TestCase

from commissaire.models import fields


class TestField(TestCase):
    """
    Tests for base Field class.
    """

    def setUp(self):
        """
        Executes before each test.
        """
        self.instance = fields.Field('test')

    def test_creation(self):
        """
        Verify creation of instance works as expected.
        """
        self.assertEquals('test', self.instance.name)
        self.assertEquals(None, self.instance.value)

    def test_value_setting(self):
        """
        Verify updating the value works.
        """
        self.assertEquals(None, self.instance.value)
        self.instance.value = 'change'
        self.assertEquals('change', self.instance.value)

    def test_rendering(self):
        """
        Verify rendering of the field works.
        """
        self.instance.value = 'change'
        rendered = self.instance.render()
        expected = {
            'name': 'test',
            'key': 'test',
            'value': 'change',
            'dir': False,
        }
        self.assertEquals(expected, rendered)


class TestIntField(TestCase):
    """
    Tests for IntField.
    """

    def setUp(self):
        """
        Executes before each test.
        """
        self.instance = fields.IntField('test')

    def test_casting(self):
        """
        Verify IntField casts properly.
        """
        self.instance.value = '10'
        self.assertEquals(10, self.instance.value)

        self.assertRaises(
            ValueError,
            self.instance._set_value,
            'error',
        )


class TestStrField(TestCase):
    """
    Tests for StrField.
    """

    def setUp(self):
        """
        Executes before each test.
        """
        self.instance = fields.StrField('test')

    def test_casting(self):
        """
        Verify StrField casts properly.
        """
        self.instance.value = 10
        self.assertEquals('10', self.instance.value)


class TestDictField(TestCase):
    """
    Tests for DictField.
    """

    def setUp(self):
        """
        Executes before each test.
        """
        self.instance = fields.DictField('test', {'a': int, 'b': str})

    def test_casting(self):
        """
        Verify StrField casts properly.
        """
        # We must have a dict
        self.assertRaises(
            TypeError,
            self.instance.value,
            "error"
        )

        # Test internal casting when a caster is provided
        self.instance.value = {'a': '10', 'b': 10}
        self.assertEquals({'a': 10, 'b': '10'}, self.instance.value)


class TestDateTimeField(TestCase):
    """
    Tests for DateTimeField.
    """

    def setUp(self):
        """
        Executes before each test.
        """
        self.instance = fields.DateTimeField('test', '%Y-%m-%d')

    def test_casting(self):
        """
        Verify DateTimeField casts properly.
        """
        # We must have a dict
        self.assertRaises(
            TypeError,
            self.instance.value,
            "error"
        )

        # Test internal casting when a caster is provided
        self.instance.value = '2016-01-01'
        self.assertEquals(datetime.datetime(2016, 1, 1), self.instance.value)
