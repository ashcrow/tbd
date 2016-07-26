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
Utilities for SSH.
"""

import os
import sys
import tempfile

from commissaire.compat.b64 import base64


class TemporarySSHKey:
    """
    An abstraction for temporary ssh keys.
    """

    def __init__(self, host, logger):
        """
        Initializes an instance of the TemporarySSHKey class.

        :param host: Host to grab ket data from.
        :type host: commissaire.handlers.models.Host
        :param logger: Logger to utilize.
        :type logger: logging.Logger
        """
        self._host = host
        self.logger = logger
        with tempfile.NamedTemporaryFile(prefix='key', delete=False) as f:
            self.path = f.name
            self.logger.debug(
                'Using {0} as the temporary key location for {1}'.format(
                    self.path, host.address))
            f.write(base64.decodestring(host.ssh_priv_key))
            f.flush()
            self.logger.info('Wrote key for {0}'.format(host.address))

    def remove(self):
        """
        Removes the temporary key file.
        """
        try:
            os.unlink(self.path)
            self.logger.debug(
                'Removed temporary key file {0}'.format(self.path))
        except:
            exc_type, exc_msg, tb = sys.exc_info()
            self.logger.warn(
                'Unable to remove the temporary key file: '
                '{0}. Exception:{1}'.format(self.path, exc_msg))
