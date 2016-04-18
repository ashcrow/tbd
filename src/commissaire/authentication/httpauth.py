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


import bcrypt
import falcon

from commissaire.authentication import Authenticator
from commissaire.compat.b64 import base64


class _HTTPBasicAuth(Authenticator):
    """
    Basic auth implementation of an authenticator.
    """

    def _decode_basic_auth(self, req):
        """
        Decodes basic auth from the header.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :returns: tuple -- (username, passphrase) or (None, None) if empty.
        :rtype: tuple
        """
        if req.auth is not None:
            if req.auth.lower().startswith('basic '):
                try:
                    decoded = tuple(base64.decodebytes(
                        req.auth[6:].encode('utf-8')).decode().split(':'))
                    self.logger.debug('Credentials given: {0}'.format(decoded))
                    return decoded
                except base64.binascii.Error:
                    self.logger.info(
                        'Bad base64 data sent. Setting to no user/pass.')
        # Default meaning no user or password
        return (None, None)

    def authenticate(self, req, resp):
        """
        Implements the authentication logic.

        :param req: Request instance that will be passed through.
        :type req: falcon.Request
        :param resp: Response instance that will be passed through.
        :type resp: falcon.Response
        :raises: falcon.HTTPForbidden
        """
        user, passwd = self._decode_basic_auth(req)
        if user is not None and passwd is not None:
            if user in self._data.keys():
                self.logger.debug('User {0} found in datastore.'.format(user))
                hashed = self._data[user]['hash'].encode('utf-8')
                try:
                    if bcrypt.hashpw(passwd.encode('utf-8'), hashed) == hashed:
                        self.logger.debug(
                            'The provided hash for user {0} '
                            'matched: {1}'.format(user, passwd))
                        return  # Authentication is good
                except ValueError:
                    pass  # Bad salt

        # Forbid by default
        raise falcon.HTTPForbidden('Forbidden', 'Forbidden')
