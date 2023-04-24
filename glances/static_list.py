# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#
# Copyright (C) 2019 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Manage the Glances server static list."""

from socket import gaierror, gethostbyname

from glances.compat import range
from glances.logger import logger


class GlancesStaticServer(object):

    """Manage the static servers list for the client browser."""

    _section = "serverlist"

    def __init__(self, config=None, args=None):
        # server_list is a list of dict (JSON compliant)
        # [ {'key': 'zeroconf name', ip': '172.1.2.3', 'port': 61209, 'cpu': 3, 'mem': 34 ...} ... ]
        # Load the configuration file
        self._server_list = self.load(config)

    def load(self, config):
        """Load the server list from the configuration file."""
        server_list = []

        if config is None:
            logger.debug("No configuration file available. Cannot load server list.")
        elif not config.has_section(self._section):
            logger.warning(
                f"No [{self._section}] section in the configuration file. Cannot load server list."
            )
        else:
            logger.info(
                f"Start reading the [{self._section}] section in the configuration file"
            )
            for i in range(1, 256):
                postfix = f'server_{str(i)}_'
                new_server = {
                    s: config.get_value(self._section, f'{postfix}{s}')
                    for s in ['name', 'port', 'alias']
                }
                if new_server['name'] is not None:
                    # Manage optionnal information
                    if new_server['port'] is None:
                        new_server['port'] = '61209'
                    new_server['username'] = 'glances'
                    # By default, try empty (aka no) password
                    new_server['password'] = ''
                    try:
                        new_server['ip'] = gethostbyname(new_server['name'])
                    except gaierror as e:
                        logger.error(f"Cannot get IP address for server {new_server['name']} ({e})")
                        continue
                    new_server['key'] = new_server['name'] + ':' + new_server['port']

                    # Default status is 'UNKNOWN'
                    new_server['status'] = 'UNKNOWN'

                    # Server type is 'STATIC'
                    new_server['type'] = 'STATIC'

                    # Add the server to the list
                    logger.debug(f"Add server {new_server['name']} to the static list")
                    server_list.append(new_server)

            # Server list loaded
            logger.info(f"{len(server_list)} server(s) loaded from the configuration file")
            logger.debug(f"Static server list: {server_list}")

        return server_list

    def get_servers_list(self):
        """Return the current server list (list of dict)."""
        return self._server_list

    def set_server(self, server_pos, key, value):
        """Set the key to the value for the server_pos (position in the list)."""
        self._server_list[server_pos][key] = value
