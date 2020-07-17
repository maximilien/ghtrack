# Copyright © 2020 IBM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, tempfile

from unittest import TestCase
from unittest.mock import patch, Mock

from cli import *

class TestCLI(TestCase):
    def setUp(self):
        self.arguments = {'--access-token': '',
                         '--credentials': './.ghtrack.yml',
                         '--users': [],
                         '--org': '',
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         'MONTH': '',
                         'commits': False,
                         'reviews': False,
                         'issues': False,
                         'stats': False}

    def test_command(self):
        self.arguments['commits'] = True
        cli = CLI(self.arguments)
        self.assertTrue(cli.command() != None)

        self.arguments['reviews'] = True
        cli = CLI(self.arguments)
        self.assertTrue(cli.command() != None)

        self.arguments['issues'] = True
        cli = CLI(self.arguments)
        self.assertTrue(cli.command() != None)

        self.arguments['stats'] = True
        cli = CLI(self.arguments)
        self.assertTrue(cli.command() != None)

    def test_dispatch(self):
        for command_name in ['commits', 'stats']:
            self.arguments[command_name] = True
            cmd = CLI(self.arguments).command()
            self.assertEqual(cmd.name(), command_name)
            self.arguments[command_name] = False # reset

class CommandTestCase:
    def setUp(self):
        self.arguments = {'--access-token': '',
                         '--credentials': './.ghtrack.yml',
                         '--users': [],
                         '--org': '',
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         'MONTH': '',
                         'commits': False,
                         'reviews': False,
                         'issues': False,
                         'stats': False}
        self.args = self.arguments

    @patch('client.GHClient')
    def __create_mock_client(self, MockGHClient):
        return MockGHClient()

    def test_verbose(self):
        self.arguments[self.command_name()] = True
        command = CLI(self.arguments).command(self.__create_mock_client())
        if self.arguments['--verbose'] == True:
            self.assertTrue(command.verbose())
        else:
            self.assertFalse(command.verbose())

    def test_name(self):
        cli = CLI(self.arguments)
        self.assertEqual(cli.command().name(), self.command_name())

class TestCommits(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['commits'] = True

    def command_name(self):
        return "commits"

    @patch('client.GHClient')
    def __create_mock_client_commits(self, MockGHClient):
        client = MockGHClient()
        client.commits.return_value = 0
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_commits()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_commits(self):
        self.arguments['commits'] = True
        cli = CLI(self.arguments)
        client = self.__create_mock_client_commits()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

if __name__ == '__main__':
    main()