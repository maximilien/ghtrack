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
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         'ORG': 'knative',
                         'MONTH': 'mar',
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
                         '--all-repos': False,
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         'ORG': 'knative',
                         'MONTH': 'mar',
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

    def test_check_month(self):
        cli = CLI(self.arguments)
        for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'September', 'October', 'November', 'December',
                      'january', 'february', 'march', 'april', 'may', 'june', 'july', 'september', 'october', 'november', 'december',
                      'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',
                      'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'sep', 'oct', 'nov', 'dec']:
            self.assertTrue(cli.command().check_month(month))
        for fake_month in ['j', 'Jany', 'Mar', 'Decem']:
            self.assertFalse(cli.command().check_month(fake_month))

    def test_check_org(self):
        cli = CLI(self.arguments)
        self.assertFalse(cli.command().check_org(None))
        self.assertFalse(cli.command().check_org(''))

    TEST_ARGS = {'--access-token': 'fake-access-token',
                         '--credentials': './.ghtrack.yml',
                         '--users': ['fake-user1', 'fake-user2'],
                         '--all-repos': False,
                         '--repos': ['fake-repo1', 'fake-repo2'],
                         '--skip-repos': ['fake-repo3'],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         'ORG': 'fake-org',
                         'MONTH': 'january',
                         'commits': False,
                         'reviews': False,
                         'issues': False,
                         'stats': True}

    def test_month(self):
        test_args = self.TEST_ARGS.copy()
        test_args['MONTH'] = 'march'
        cli = CLI(test_args)
        self.assertEqual(cli.command().month(), "march")

    def test_users(self):
        cli = CLI(self.TEST_ARGS.copy())
        self.assertEqual(cli.command().users(), ['fake-user1', 'fake-user2'])

    def test_users_empty(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--users'] = []
        cli = CLI(test_args)
        self.assertEqual(cli.command().users(), [])

    def test_org(self):
        cli = CLI(self.TEST_ARGS.copy())
        self.assertEqual(cli.command().org(), 'fake-org')

    def test_org_empty(self):
        test_args = self.TEST_ARGS.copy()
        test_args['ORG'] = ''
        cli = CLI(test_args)
        self.assertEqual(cli.command().org(), '')

    def test_repos(self):
        cli = CLI(self.TEST_ARGS.copy())
        self.assertEqual(cli.command().repos(), ['fake-repo1', 'fake-repo2'])

    def test_repos_empty(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--repos'] = []
        cli = CLI(test_args)
        self.assertEqual(cli.command().repos(), [])

    def test_skip_repos(self):
        cli = CLI(self.TEST_ARGS.copy())
        self.assertEqual(cli.command().skip_repos(), ['fake-repo3'])

    def test_skip_repos_empty(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--skip-repos'] = []
        cli = CLI(test_args)
        self.assertEqual(cli.command().skip_repos(), [])

    def test_all_repos_False(self):
        cli = CLI(self.TEST_ARGS.copy())
        self.assertEqual(cli.command().all_repos(), False)

    def test_all_repos_True(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--all-repos'] = True
        cli = CLI(test_args)
        self.assertEqual(cli.command().all_repos(), True)

    def test_cmd_line(self):
        for cmd in ["commits", "reviews", "issues"]:
            expected_cmd_line = "{cmd} january fake-org --users=fake-user1,fake-user2 --repos=fake-repo1,fake-repo2 --skip-repos=fake-repo3".format(cmd=cmd)
            test_args = self.TEST_ARGS.copy()
            test_args['stats'] = False
            if cmd == "commits":
                test_args['commits'] = True
            elif cmd == "reviews":
                test_args['reviews'] = True
            elif cmd == 'issues':
                test_args['issues'] = True
            else:
                test_args['stats'] = True
            cli = CLI(test_args)
            self.assertEqual(cli.command().cmd_line(), expected_cmd_line)

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