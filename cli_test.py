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

import io, os, tempfile

from unittest import TestCase
from unittest.mock import patch, Mock

from datetime import datetime

from cli import *

class TestCLI(TestCase):
    def setUp(self):
        self.arguments = {'--access-token': 'fake-access-token',
                         '--credentials': './.ghtrack.yml',
                         '--users': [],
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         '--all-repos': False,
                         '--summarize': False,
                         '--show-all-stats': False,
                         '--rate-limit': False,
                         '--rate-limit-random': False,
                         '--state': 'closed',
                         '--output': 'text',
                         '--file': '',
                         '--output': 'text',
                         '--file': '',
                         'ORG': 'knative',
                         'MONTH': 'mar',
                         'commits': False,
                         'prs': False,
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

        self.arguments['prs'] = True
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
        self.arguments = {'--access-token': 'fake-access-token',
                         '--credentials': './.ghtrack.yml',
                         '--users': [],
                         '--all-repos': False,
                         '--repos': [],
                         '--skip-repos': [],
                         '--help': False,
                         '--verbose': False,
                         '--version': False,
                         '--all-repos': False,
                         '--summarize': False,
                         '--show-all-stats': False,
                         '--rate-limit': False,
                         '--rate-limit-random': False,
                         '--state': 'closed',
                         '--output': 'text',
                         '--file': '',
                         'ORG': 'knative',
                         'MONTH': 'mar',
                         'commits': False,
                         'reviews': False,
                         'prs': False,
                         'issues': False,
                         'stats': False}
        self.args = self.arguments

    @patch('client.GHClient')
    def __create_mock_client(self, MockGHClient):
        return MockGHClient()

    @patch('client.GHClient')
    def __create_mock_client_get_repos(self, MockGHClient):
        client = MockGHClient()
        class Repo:
            def __init__(self, name):
                self.name = name
        client.repos.return_value = [Repo('fake-repo1'), Repo('fake-repo2'), Repo('fake-repo3')]
        return client

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

    def test_fetch_repos(self):
        self.arguments['--repos'] = []
        self.arguments['--skip-repos'] = []
        self.arguments['--all-repos'] = True
        self.org = 'knative'
        client = self.__create_mock_client_get_repos()
        cli = CLI(self.arguments)
        cli.command(client).fetch_repos()
        self.assertTrue(len(self.arguments['--repos']) == 3)
        self.assertTrue(len(self.arguments['--skip-repos']) == 0)
        for repo_name in ['fake-repo1', 'fake-repo2', 'fake-repo3']:
            self.assertTrue(repo_name in self.arguments['--repos'])

    TEST_ARGS = {'--access-token': 'fake-access-token',
                 '--credentials': './.ghtrack.yml',
                 '--users': ['fake-user1', 'fake-user2'],
                 '--all-repos': False,
                 '--repos': ['fake-repo1', 'fake-repo2'],
                 '--skip-repos': ['fake-repo3'],
                 '--help': False,
                 '--verbose': False,
                 '--version': False,
                 '--summarize': False,
                 '--show-all-stats': False,
                 '--rate-limit': False,
                 '--rate-limit-random': False,
                 '--commits': False,
                 '--prs': False,
                 '--reviews': False,
                 '--issues': False,
                 '--state': 'closed',
                 '--output': None,
                 '--file': None,
                 'ORG': 'fake-org',
                 'MONTH': 'january',
                 'commits': False,
                 'reviews': False,
                 'prs': False,
                 'issues': False,
                 'stats': True}

    def test_name(self):
        cli = CLI(self.arguments)
        self.assertEqual(cli.command().name(), self.command_name())

    def test_cmd_line(self):
        for cmd in ["commits", "reviews", "issues"]:
            expected_cmd_line = "{cmd} january fake-org --users=fake-user1,fake-user2 --repos=fake-repo1,fake-repo2 --skip-repos=fake-repo3".format(cmd=cmd)
            test_args = self.TEST_ARGS.copy()
            test_args['stats'] = False
            if cmd == "commits":
                test_args['commits'] = True
            elif cmd == "reviews":
                test_args['reviews'] = True
            elif cmd == "prs":
                test_args['prs'] = True
            elif cmd == 'issues':
                test_args['issues'] = True
            else:
                test_args['stats'] = True
            cli = CLI(test_args)
            self.assertEqual(cli.command().cmd_line(), expected_cmd_line)

    def test_check_month(self):
        cli = CLI(self.TEST_ARGS)
        self.assertTrue(cli.command().check_month(cli.command().month()))
        self.assertFalse(cli.command().check_month('fake-month'))

    def test_check_org(self):
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_org(cli.command().org()))
        self.assertFalse(cli.command().check_org(''))
        self.assertFalse(cli.command().check_org(None))

    def test_check_state(self):
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_state('open'))
        self.assertTrue(cli.command().check_state('closed'))
        self.assertFalse(cli.command().check_state('fake-state'))
        self.assertFalse(cli.command().check_state(''))
        self.assertFalse(cli.command().check_state(None))

    def test_check_required_options(self):
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_required_options())

        test_args['MONTH'] = 'fake-month'
        self.assertFalse(cli.command().check_required_options())

        test_args['ORG'] = ''
        self.assertFalse(cli.command().check_required_options())

        test_args['--state'] = 'fake-state'
        self.assertFalse(cli.command().check_required_options())

    def test_println(self):
        stdout = sys.stdout
        sys.stdout = io.StringIO()
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        cli.command().println("fake-println\n")
        self.assertTrue("fake-println\n" in sys.stdout.getvalue())
        sys.stdout = stdout

    def test_print(self):
        stdout = sys.stdout
        sys.stdout = io.StringIO()
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        cli.command().print("fake-print")
        self.assertTrue("fake-print" in sys.stdout.getvalue())
        sys.stdout = stdout

    def test_warn(self):
        stdout = sys.stdout
        sys.stdout = io.StringIO()
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        cli.command().warn("fake-warn")
        self.assertTrue("fake-warn" in sys.stdout.getvalue())
        sys.stdout = stdout

    def test_verbose(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--verbose'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().verbose())

    def test_state(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--state'] = 'open'
        cli = CLI(test_args)
        self.assertEqual(cli.command().state(), 'open')

    def test_year(self):
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        self.assertEqual(cli.command().year(), datetime.now().year)

    def test_start_date(self):
        test_args = self.TEST_ARGS.copy()
        test_args['MONTH'] = 'march'
        cli = CLI(test_args)
        year = cli.command().year()
        self.assertEqual(cli.command().start_date(), datetime(year=year, month=3, day=1))

    def test_end_date(self):
        test_args = self.TEST_ARGS.copy()
        test_args['MONTH'] = 'march'
        cli = CLI(test_args)
        year = cli.command().year()
        self.assertEqual(cli.command().end_date(), datetime(year=year, month=3, day=31))

    def test_month_last_day(self):
        test_args = self.TEST_ARGS.copy()
        test_args['MONTH'] = 'march'
        cli = CLI(test_args)
        self.assertEqual(cli.command().month_last_day(), 31)

        test_args['MONTH'] = 'November'
        cli = CLI(test_args)
        self.assertEqual(cli.command().month_last_day(), 30)

    def test_month_number(self):
        test_args = self.TEST_ARGS.copy()
        cli = CLI(test_args)
        self.assertEqual(cli.command().month_number(), 1)

        test_args['MONTH'] = 'march'
        cli = CLI(test_args)
        self.assertEqual(cli.command().month_number(), 3)

    def test_output(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--output'] = 'CSV'
        cli = CLI(test_args)
        self.assertEqual(cli.command().output(), 'CSV')

    def test_file(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--file'] = 'fake/output/file'
        cli = CLI(test_args)
        self.assertEqual(cli.command().file(), 'fake/output/file')

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
        self.assertFalse(cli.command().all_repos())

    def test_all_repos_True(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--all-repos'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().all_repos())

    def test_show_all_stats_True(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--show-all-stats'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().show_all_stats())

    def test_show_all_stats_False(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--show-all-stats'] = False
        cli = CLI(test_args)
        self.assertFalse(cli.command().show_all_stats())

    def test_summarize(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--summarize'] = False
        cli = CLI(test_args)
        self.assertFalse(cli.command().summarize())

        test_args = self.TEST_ARGS.copy()
        test_args['--summarize'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().summarize())

    def test_rate_limit(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = False
        cli = CLI(test_args)
        self.assertFalse(cli.command().rate_limit())

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().rate_limit())

    def test_rl_max(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-max'] = 1
        cli = CLI(test_args)
        self.assertEqual(cli.command().rl_max(), 1)

    def test_rl_sleep(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = '1m'
        cli = CLI(test_args)
        self.assertEqual(cli.command().rl_sleep(), '1m')

    def test_check_rl_max(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-max'] = 0
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_rl_max())

        test_args['--rate-limit'] = True
        test_args['--rl-max'] = 1
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_rl_max())

        test_args['--rate-limit'] = True
        test_args['--rl-max'] = -1
        cli = CLI(test_args)
        self.assertFalse(cli.command().check_rl_max())

    def test_check_rl_sleep(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = ''
        cli = CLI(test_args)
        self.assertFalse(cli.command().check_rl_sleep())

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = 1
        cli = CLI(test_args)
        self.assertFalse(cli.command().check_rl_sleep())

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = 'm'
        cli = CLI(test_args)
        self.assertFalse(cli.command().check_rl_sleep())

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = '1m'
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_rl_sleep())
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.sleep(), 60)

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = '1h'
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_rl_sleep())
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.sleep(), 3600)

        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = '2d'
        cli = CLI(test_args)
        self.assertTrue(cli.command().check_rl_sleep())
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.sleep(), 2*24*3600)

    def test_rate_limit_False(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = False
        cli = CLI(test_args)
        self.assertFalse(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.max_calls(), 0)
        self.assertEqual(cli.command().rate_limit_data.sleep(), 0)

    def test_rate_limit_True(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        cli = CLI(test_args)
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.max_calls(), 100)
        self.assertEqual(cli.command().rate_limit_data.sleep(), 30*60)

    def test_rate_limit_bad_rl_max(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-max'] = -1
        cli = CLI(test_args)
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.max_calls(), 100)

    def test_rate_limit_bad_rl_sleep(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-sleep'] = ''
        cli = CLI(test_args)
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().rate_limit_data.sleep(), 30*60)

    def test_rate_limit_True_values(self):
        test_args = self.TEST_ARGS.copy()
        test_args['--rate-limit'] = True
        test_args['--rl-max'] = 200
        test_args['--rl-sleep'] = '1h'
        cli = CLI(test_args)
        self.assertTrue(cli.command().rate_limit_data.enabled())
        self.assertEqual(cli.command().client.rate_limit_data.max_calls(), 200)
        self.assertEqual(cli.command().client.rate_limit_data.sleep(), 1*60*60)

class TestCommits(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['commits'] = True

    def command_name(self):
        return "commits"

    @patch('client.GHClient')
    def __create_mock_client_commits(self, MockGHClient):
        client = MockGHClient()
        client.commits_count.return_value = 0
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_commits()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_commits(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_commits()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

class TestReviews(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['reviews'] = True

    def command_name(self):
        return "reviews"

    @patch('client.GHClient')
    def __create_mock_client_reviews(self, MockGHClient):
        client = MockGHClient()
        client.reviews_count.return_value = 0
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_reviews()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_reviews(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_reviews()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_reviews(self):
        self.arguments['--summarize'] = True
        cli = CLI(self.arguments)
        client = self.__create_mock_client_reviews()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

class TestPRs(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['prs'] = True

    def command_name(self):
        return "prs"

    @patch('client.GHClient')
    def __create_mock_client_prs(self, MockGHClient):
        client = MockGHClient()
        client.prs_count.return_value = 0
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_prs()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_prs(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_prs()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_prs_summarize(self):
        self.arguments['--summarize'] = True
        cli = CLI(self.arguments)
        client = self.__create_mock_client_prs()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

class TestIssues(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['issues'] = True

    def command_name(self):
        return "issues"

    @patch('client.GHClient')
    def __create_mock_client_issues(self, MockGHClient):
        client = MockGHClient()
        client.issues_count.return_value = 0
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_issues()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_issues(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_issues()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_issues_summarize(self):
        self.arguments['--summarize'] = True
        cli = CLI(self.arguments)
        client = self.__create_mock_client_issues()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

class TestStats(CommandTestCase, TestCase):
    def setUp(self):
        super().setUp()
        self.arguments['stats'] = True
        self.arguments['--commits'] = True
        self.arguments['--prs'] = True
        self.arguments['--reviews'] = True
        self.arguments['--issues'] = True

    def command_name(self):
        return "stats"

    @patch('client.GHClient')
    def __create_mock_client_stats(self, MockGHClient):
        client = MockGHClient()
        client.issues_count.return_value = 0
        client.commits_count.return_value = 1
        client.reviews_count.return_value = 2
        client.prs_count.return_value = 3
        return client

    def test_execute(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_stats()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_stats(self):
        cli = CLI(self.arguments)
        client = self.__create_mock_client_stats()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

    def test_stats_summarize(self):
        self.arguments['--summarize'] = True
        cli = CLI(self.arguments)
        client = self.__create_mock_client_stats()
        rc = cli.command(client).execute()
        self.assertEqual(rc, 0)

if __name__ == '__main__':
    main()