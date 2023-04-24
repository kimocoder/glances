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

"""CouchDB interface class."""

import sys
from datetime import datetime

from glances.logger import logger
from glances.exports.glances_export import GlancesExport

import couchdb
import couchdb.mapping


class Export(GlancesExport):

    """This class manages the CouchDB export module."""

    def __init__(self, config=None, args=None):
        """Init the CouchDB export IF."""
        super(Export, self).__init__(config=config, args=args)

        # Mandatories configuration keys (additional to host and port)
        self.db = None

        # Optionals configuration keys
        self.user = None
        self.password = None

        # Load the Cassandra configuration file section
        self.export_enable = self.load_conf('couchdb',
                                            mandatories=['host', 'port', 'db'],
                                            options=['user', 'password'])
        if not self.export_enable:
            sys.exit(2)

        # Init the CouchDB client
        self.client = self.init()

    def init(self):
        """Init the connection to the CouchDB server."""
        if not self.export_enable:
            return None

        if self.user is None:
            server_uri = f'http://{self.host}:{self.port}/'
        else:
            server_uri = f'http://{self.user}:{self.password}@{self.host}:{self.port}/'

        try:
            s = couchdb.Server(server_uri)
        except Exception as e:
            logger.critical(f"Cannot connect to CouchDB server {server_uri} ({e})")
            sys.exit(2)
        else:
            logger.info(f"Connected to the CouchDB server {server_uri}")

        try:
            s[self.db]
        except Exception as e:
            # Database did not exist
            # Create it...
            s.create(self.db)
        else:
            logger.info(f"There is already a {self.db} database")

        return s

    def database(self):
        """Return the CouchDB database object"""
        return self.client[self.db]

    def export(self, name, columns, points):
        """Write the points to the CouchDB server."""
        logger.debug(f"Export {name} stats to CouchDB")

        # Create DB input
        data = dict(zip(columns, points))

        # Set the type to the current stat name
        data['type'] = name
        data['time'] = couchdb.mapping.DateTimeField()._to_json(datetime.now())

        # Write input to the CouchDB database
        # Result can be view: http://127.0.0.1:5984/_utils
        try:
            self.client[self.db].save(data)
        except Exception as e:
            logger.error(f"Cannot export {name} stats to CouchDB ({e})")
