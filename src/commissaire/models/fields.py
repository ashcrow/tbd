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
All fields for orm like instances.
"""

import datetime
import json


class Field(object):
    """
    Base class for all fields.
    """

    def __init__(self, name, hidden=False):
        """
        Initializes a new Field instance.

        :param name: The name of the field
        :type name: str
        :param hidden: If the field should be hidden during json dumps.
        :type hidden: bool
        """
        self.name = name
        self.hidden = hidden
        self._value = None

    @property
    def json(self):
        """
        Returns a json version of the field.

        :returns: JSON representation.
        :rtype: str
        """
        if self.hidden:
            return json.dumps({})
        return json.dumps({self.name: self._value})

    @property
    def value(self):
        """
        Returns the value of the field.

        :returns: The value of the field
        :rtype: mixed
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Sets the field value.

        :param value: The value to use.
        :type value: mixed
        """
        self._set_value(value)

    def _set_value(self, value):
        """
        Internal method that sets the field value.

        :param value: The value to use.
        :type value: mixed
        """
        self._value = value

    def render(self):
        """
        Renders the field into a structure that can be persisted to etcd.

        :returns: A structure to be used with etcd
        :rtype: dict
        """
        return {
            'name': self.name,
            'key': self.name,
            'value': self._value,
            'dir': False,
        }


class _CastField(Field):  # pragma: no cover
    """
    Base class for all Fields which force specific types.
    """
    _caster = None
    _default_empty = None

    def _set_value(self, value):
        """
        Internal method that sets the field value.

        :param value: The value to use.
        :type value: mixed
        """
        if not value:
            self._value = self._default_empty
        else:
            self._value = self._caster(value)


class IntField(_CastField):
    """
    A Field that forces a cast to an int.
    """
    _caster = int
    _default_empty = None


class StrField(_CastField):
    """
    A Field that forces a cast to a str.
    """
    _caster = str
    _default_empty = ''


class DateTimeField(Field):
    """
    A Field that forces a cast to a datetime.datetime instance.
    """

    def __init__(self, name, datefmt, *args, **kwargs):
        """
        Initializes an instance of DateTimeField.

        :param name: The name of the field
        :type name: str
        :param datefmt: The datetime format to parse to/from.
        :type datefmt: str
        :param args: All non-keyword arguments.
        :type args: list
        :param kwargs: All keyword arguments.
        :type kwargs: dict
        """
        super(DateTimeField, self).__init__(name, *args, **kwargs)
        self._datefmt = datefmt

    def _set_value(self, value):
        """
        Internal method that sets the field value.

        :param value: The value to use.
        :type value: str or datetime.datetime
        :raises: TypeError
        """
        if type(value) is datetime.datetime:
            self._value = value
        elif not value:
            self._value = None
        else:
            self._value = datetime.datetime.strptime(value, self._datefmt)

    @property
    def json(self):
        """
        Returns a json version of the field.

        :returns: JSON representation.
        :rtype: str
        """
        if self.hidden:
            return json.dumps({})
        if not self._value:
            return json.dumps({self.name: None})
        return json.dumps({
            self.name: datetime.datetime.strftime(self._value, self._datefmt),
        })

    def render(self):
        """
        Renders the field into a structure that can be persisted to etcd.

        :returns: A structure to be used with etcd
        :rtype: dict
        """
        if not self._value:
            value = None
        else:
            value = datetime.datetime.strftime(self._value, self._datefmt),
        return {
            'name': self.name,
            'key': self.name,
            'value': value,
            'dir': False,
        }


class DictField(Field):
    """
    A Field that only accepts dicts.
    """

    def __init__(self, name, caster={}, *args, **kwargs):
        """
        Initializes an instance of DictField.

        :param args: All non-keyword arguments.
        :type args: list
        :param caster: A caster structure for casting dictionary items.
        :type caster: dict
        :param kwargs: All keyword arguments.
        :type kwargs: dict
        """
        super(DictField, self).__init__(name, *args, **kwargs)
        self._caster = caster
        self._value = {}

    @property
    def json(self):
        """
        Returns a json version of the field.

        .. note::

           DictField serializes the dictionary without the name.

        :returns: JSON representation.
        :rtype: str
        """
        if self.hidden:
            return json.dumps({})
        return json.dumps(self._value)

    def _set_value(self, value):
        """
        Internal method that sets the field value.

        :param value: The value to use.
        :type value: dict
        :raises: TypeError
        """
        if type(value) != dict:
            raise TypeError('Must use dict. Provided: {0}'.format(type(value)))

        # Force casting if we were given a caster.
        if self._caster:
            for x in value.keys():
                caster = self._caster.get(x, None)
                if callable(caster):
                    value[x] = caster(value[x])

        super(DictField, self)._set_value(value)

    def render(self):
        """
        Renders the field into a structure that can be persisted to etcd.

        :returns: A list of structures to be used with etcd
        :rtype: list
        """
        rendered = []
        for x in self._value.keys():
            rendered.append({
                'name': self.name,
                'key': '{0}/{1}'.format(self.name, x),
                'value': self._value[x],
                'dir': True,
            })
        return rendered
