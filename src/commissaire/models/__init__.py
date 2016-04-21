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
ORM like interface for etcd.

.. note::

   Most of this code is originally from https://github.com/ashcrow/etcdobj and
   has been pulled in and relicensed to GPLv3+ with the authors permission.
"""

import json

import etcd

from commissaire.models.fields import Field


class _Server(object):
    """
    Parent class for all Server implementations.
    """

    def __init__(self, client, *args, **kwargs):
        """
        Creates a new instance of a Server implementation.

        :param client: The etcd client to use.
        :type client: object
        :param args: All other non-keyword arguments.
        :type args: list
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :raises: ValueError
        """
        self.client = None
        self._verify_client(client)

    def _verify_client(self, client):
        """
        Does basic validation that the client can be used.

        :param client: The client to check.
        :type client: object
        :raises: ValueError
        """
        missing = []
        for method in ('write', 'read', 'delete'):
            if not callable(getattr(client, method, None)):
                missing.append(method)

        if missing:
            raise ValueError('The following methods are missing from the '
                             'client: {0}'.format(', '.join(missing)))

        self.client = client

    def save(self, obj):
        """
        Save an object.

        :param obj: An instance that subclasses EtcdObj
        :type obj: EtcdObj
        :returns: The same instance
        :rtype: EtcdObj
        """
        for item in obj.render():
            self.client.write(item['key'], item['value'], quorum=True)
        return obj

    def read(self, obj, must_exist=False):
        """
        Retrieve an object.

        :param obj: An instance that subclasses EtcdObj
        :type obj: EtcdObj
        :returns: A filled out instance
        :rtype: EtcdObj
        """
        exists = False  # If at least 1 key exists for this object
        for item in obj.render():
            try:
                etcd_resp = self.client.read(item['key'], quorum=True)
                value = etcd_resp.value
                exists = True
            except etcd.EtcdKeyNotFound:
                # Default to None if the key doesn't exist
                value = None
            if item['dir']:
                key = item['key'].split('/')[-1]
                dct = getattr(obj, item['name'])
                dct[key] = value
            else:
                attr = object.__getattribute__(obj, item['name'])
                attr.value = value
        if must_exist and not exists:
            raise Exception('{0} does not exist in Etcd'.format(obj))
        return obj


class Server(_Server):
    """
    Server implementation which creates an etcd.Client instance
    as its client.
    """

    def __init__(self, etcd_kwargs={}, *args, **kwargs):
        """
        Creates a new instance of Server.

        :param etcd_kwargs: The keyword arguments used to create an etcd.Client
        :type client: dict
        :param args: All other non-keyword arguments.
        :type args: list
        :param kwargs: All other keyword arguments.
        :type kwargs: dict
        :raises: ValueError
        """
        super(Server, self).__init__(
            etcd.Client(**etcd_kwargs), *args, **kwargs)


class EtcdObj(object):
    """
    Class all objects which want to persist to etcd must subclass.
    """

    _fields = {}

    def __new__(cls, **kwargs):
        """
        Creates a new instance.

        :param kwargs: All keyword arguments.
        :type kwargs: dict
        :returns: The new instance
        :rtype: EtcdObj
        """
        cls = super(EtcdObj, cls).__new__(cls)
        for key in dir(cls):
            if not key.startswith('_'):
                attr = getattr(cls, key)
                if issubclass(attr.__class__, Field):
                    cls._fields[key] = attr

        return cls

    def __init__(self, **kwargs):  # pragma: no cover
        """
        Initializes a new instance. Required for __new__.

        :param kwargs: All keyword arguments.
        :type kwargs: dict
        """
        if 'extend' in kwargs.keys():
            self.extend(kwargs['extend'])
        for key in kwargs.keys():
            if key in self._fields.keys():
                self._fields[key].value = kwargs[key]

    def extend(self, path):
        """
        Extends the key path.

        :param path: The key path (appended to __name__)
        :type path: str
        """
        object.__setattr__(self, '__name__', '/'.join((self.__name__, path)))

    def __setattr__(self, name, value):
        """
        Overridden setattr to catch fields or pass along if not a field.

        :param name: The name of the field.
        :type name: str
        :param value: The value to set on name.
        :type value: any
        """
        if name in self._fields.keys():
            self._fields[name].value = value
        else:
            object.__setattr__(self, name, value)
        # attr = object.__getattribute__(self, name)
        # if name in self._fields:
        #     attr.value = value
        # else:
        #     object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        """
        Overridden  getattribute to catch fields or pass along if not a field.

        :param name: The name of the field.
        :type name: str
        :returns: The value of the field or attribute
        :rtype: any
        :raises: AttributeError
        """
        if name in object.__getattribute__(self, '_fields').keys():
            return self._fields[name].value
        return object.__getattribute__(self, name)

    def render(self):
        """
        Renders the instance into a structure for settings in etcd.

        :returns: The structure to use for setting.
        :rtype: list(dict{key=str,value=any})
        """
        rendered = []
        for name, attr in object.__getattribute__(self, '_fields').items():
            items = attr.render()
            if type(items) != list:
                items = [items]
            for i in items:
                i['key'] = '/{0}/{1}'.format(self.__name__, i['key'])
                rendered.append(i)
        return rendered

    @property
    def json(self):
        """
        Dumps the entire object as a json structure.
        """
        print self.__name__, self
        data = {}
        for name, attr in object.__getattribute__(self, '_fields').items():
            # FIXME: This is dumb :-)
            if not attr.hidden:
                data[attr.name] = json.loads(attr.json)
                # Flatten if needed
                if attr.name in data[attr.name].keys():
                    data[attr.name] = data[attr.name][attr.name]
        return json.dumps(data)
