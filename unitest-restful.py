#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Glances - An eye on your system
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

"""Glances unitary tests suite for the RESTful API."""


import shlex
import subprocess
import time
import numbers
import unittest

from glances import __version__
from glances.compat import text_type

import requests

SERVER_PORT = 61234
API_VERSION = 3
URL = f"http://localhost:{SERVER_PORT}/api/{API_VERSION}"
pid = None

# Unitest class
# ==============
print(f'RESTful API unitary tests for Glances {__version__}')


class TestGlances(unittest.TestCase):
    """Test Glances class."""

    def setUp(self):
        """The function is called *every time* before test_*."""
        print('\n' + '=' * 78)

    def http_get(self, url, deflate=False):
        """Make the request"""
        return (
            requests.get(url, stream=True, headers={'Accept-encoding': 'deflate'})
            if deflate
            else requests.get(url, headers={'Accept-encoding': 'identity'})
        )

    def test_000_start_server(self):
        """Start the Glances Web Server."""
        global pid

        print('INFO: [TEST_000] Start the Glances Web Server')
        cmdline = f"python -m glances -w -p {SERVER_PORT}"
        print(f"Run the Glances Web Server on port {SERVER_PORT}")
        args = shlex.split(cmdline)
        pid = subprocess.Popen(args)
        print("Please wait 5 seconds...")
        time.sleep(5)

        self.assertTrue(pid is not None)

    def test_001_all(self):
        """All."""
        method = "all"
        print('INFO: [TEST_001] Get all stats')
        print(f"HTTP RESTful request: {URL}/{method}")
        req = self.http_get(f"{URL}/{method}")

        self.assertTrue(req.ok)

    def test_001a_all_deflate(self):
        """All."""
        method = "all"
        print('INFO: [TEST_001a] Get all stats (with Deflate compression)')
        print(f"HTTP RESTful request: {URL}/{method}")
        req = self.http_get(f"{URL}/{method}", deflate=True)

        self.assertTrue(req.ok)
        self.assertTrue(req.headers['Content-Encoding'] == 'deflate')

    def test_002_pluginslist(self):
        """Plugins list."""
        method = "pluginslist"
        print('INFO: [TEST_002] Plugins list')
        print(f"HTTP RESTful request: {URL}/{method}")
        req = self.http_get(f"{URL}/{method}")

        self.assertTrue(req.ok)
        self.assertIsInstance(req.json(), list)
        self.assertIn('cpu', req.json())

    def test_003_plugins(self):
        """Plugins."""
        method = "pluginslist"
        print('INFO: [TEST_003] Plugins')
        plist = self.http_get(f"{URL}/{method}")

        for p in plist.json():
            print(f"HTTP RESTful request: {URL}/{p}")
            req = self.http_get(f"{URL}/{p}")
            self.assertTrue(req.ok)
            if p in ('uptime', 'now'):
                self.assertIsInstance(req.json(), text_type)
            elif p in ('fs', 'percpu', 'sensors', 'alert', 'processlist', 'diskio',
                       'hddtemp', 'batpercent', 'network', 'folders', 'amps', 'ports',
                       'irq', 'wifi', 'gpu'):
                self.assertIsInstance(req.json(), list)
            elif p not in ('psutilversion', 'help'):
                self.assertIsInstance(req.json(), dict)

    def test_004_items(self):
        """Items."""
        method = "cpu"
        print('INFO: [TEST_004] Items for the CPU method')
        ilist = self.http_get(f"{URL}/{method}")

        for i in ilist.json():
            print(f"HTTP RESTful request: {URL}/{method}/{i}")
            req = self.http_get(f"{URL}/{method}/{i}")
            self.assertTrue(req.ok)
            self.assertIsInstance(req.json(), dict)
            print(req.json()[i])
            self.assertIsInstance(req.json()[i], numbers.Number)

    def test_005_values(self):
        """Values."""
        method = "processlist"
        print('INFO: [TEST_005] Item=Value for the PROCESSLIST method')
        print(f"{URL}/{method}/pid/0")
        req = self.http_get(f"{URL}/{method}/pid/0")

        self.assertTrue(req.ok)
        self.assertIsInstance(req.json(), dict)

    def test_006_all_limits(self):
        """All limits."""
        method = "all/limits"
        print('INFO: [TEST_006] Get all limits')
        print(f"HTTP RESTful request: {URL}/{method}")
        req = self.http_get(f"{URL}/{method}")

        self.assertTrue(req.ok)
        self.assertIsInstance(req.json(), dict)

    def test_007_all_views(self):
        """All views."""
        method = "all/views"
        print('INFO: [TEST_007] Get all views')
        print(f"HTTP RESTful request: {URL}/{method}")
        req = self.http_get(f"{URL}/{method}")

        self.assertTrue(req.ok)
        self.assertIsInstance(req.json(), dict)

    def test_008_plugins_limits(self):
        """Plugins limits."""
        method = "pluginslist"
        print('INFO: [TEST_008] Plugins limits')
        plist = self.http_get(f"{URL}/{method}")

        for p in plist.json():
            print(f"HTTP RESTful request: {URL}/{p}/limits")
            req = self.http_get(f"{URL}/{p}/limits")
            self.assertTrue(req.ok)
            self.assertIsInstance(req.json(), dict)

    def test_009_plugins_views(self):
        """Plugins views."""
        method = "pluginslist"
        print('INFO: [TEST_009] Plugins views')
        plist = self.http_get(f"{URL}/{method}")

        for p in plist.json():
            print(f"HTTP RESTful request: {URL}/{p}/views")
            req = self.http_get(f"{URL}/{p}/views")
            self.assertTrue(req.ok)
            self.assertIsInstance(req.json(), dict)

    def test_010_history(self):
        """History."""
        method = "history"
        print('INFO: [TEST_010] History')
        print(f"HTTP RESTful request: {URL}/cpu/{method}")
        req = self.http_get(f"{URL}/cpu/{method}")
        self.assertIsInstance(req.json(), dict)
        self.assertIsInstance(req.json()['user'], list)
        self.assertTrue(len(req.json()['user']) > 0)
        print(f"HTTP RESTful request: {URL}/cpu/{method}/3")
        req = self.http_get(f"{URL}/cpu/{method}/3")
        self.assertIsInstance(req.json(), dict)
        self.assertIsInstance(req.json()['user'], list)
        self.assertTrue(len(req.json()['user']) > 1)
        print(f"HTTP RESTful request: {URL}/cpu/system/{method}")
        req = self.http_get(f"{URL}/cpu/system/{method}")
        self.assertIsInstance(req.json(), dict)
        self.assertIsInstance(req.json()['system'], list)
        self.assertTrue(len(req.json()['system']) > 0)
        print(f"HTTP RESTful request: {URL}/cpu/system/{method}/3")
        req = self.http_get(f"{URL}/cpu/system/{method}/3")
        self.assertIsInstance(req.json(), dict)
        self.assertIsInstance(req.json()['system'], list)
        self.assertTrue(len(req.json()['system']) > 1)

    def test_011_issue1401(self):
        """Check issue #1401."""
        method = "network/interface_name"
        print('INFO: [TEST_011] Issue #1401')
        req = self.http_get(f"{URL}/{method}")
        self.assertTrue(req.ok)
        self.assertIsInstance(req.json(), dict)
        self.assertIsInstance(req.json()['interface_name'], list)

    def test_999_stop_server(self):
        """Stop the Glances Web Server."""
        print('INFO: [TEST_999] Stop the Glances Web Server')

        print("Stop the Glances Web Server")
        pid.terminate()
        time.sleep(1)

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
