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
CherryPy plugin for storing objects.
"""

import sys

from cherrypy.process import plugins

from commissaire import models


class CherryPyStorePlugin(plugins.SimplePlugin):

    def __init__(self, bus, store_kwargs):
        """
        Creates a new instance of the CherryPyStorePlugin.

        :param bus: The CherryPy bus.
        :type bus: cherrypy.process.wspbus.Bus
        :param store_kwargs: Keyword arguments used to make the Client.
        :type store_kwargs: dict
        """
        plugins.SimplePlugin.__init__(self, bus)
        self.store_kwargs = store_kwargs
        self.store = None

    def _get_store(self):
        """
        Returns an instance of the store. If one has not been created this call
        will also create the client using the self.store_kwargs.

        :returns: The store.
        :rtype: etcd.Client
        """
        if not self.store:
            self.store = models.Server(etcd_kwargs=self.store_kwargs)
        return self.store

    def start(self):
        """
        Starts the plugin.
        """
        self.bus.log('Starting up Store access')
        self.bus.subscribe("store-save", self.store_save)
        self.bus.subscribe("store-get", self.store_get)
        self.bus.subscribe("store-delete", self.store_delete)

    def stop(self):
        """
        Stops the plugin.
        """
        self.bus.log('Stopping down Store access')
        self.bus.unsubscribe("store-save", self.store_save)
        self.bus.unsubscribe("store-get", self.store_get)
        self.bus.unsubscribe("store-delete", self.store_delete)

    def store_save(self, entity, **kwargs):
        """
        Saves a model to the store.

        :param entity: The model entity to save.
        :type entity: models.EtcdObj
        :returns: The stores response and any errors that may have occured
        :rtype: tuple(model.EtcdObj, Exception)
        """
        try:
            store = self._get_store()
            return (store.save(entity), None)
        except:
            _, exc, _ = sys.exc_info()
            return ([], exc)

    def store_get(self, entity):
        """
        Retrieves a model from the store.

        :param entity: The entity to fill.
        :type entity: models.EtcdObj
        :returns: The stores response and any errors that may have occured
        :rtype: tuple(etcd.EtcdResult, Exception)
        """
        try:
            store = self._get_store()
            return (store.read(entity, must_exist=True), None)
        except:
            _, exc, _ = sys.exc_info()
            return ([], exc)

    def store_delete(self, entity):
        """
        Deletes a model from the store.

        :param entity: The entity to delete.
        :type entity: models.EtcdObj
        :returns: The stores response and any errors that may have occured
        :rtype: tuple(etcd.EtcdResult, Exception)
        """
        try:
            store = self._get_store()
            return (store.delete(entity), None)
        except:
            _, exc, _ = sys.exc_info()
            return ([], exc)
