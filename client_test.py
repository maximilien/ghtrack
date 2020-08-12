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

import os, cli, unittest

from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from client import *

class TestGHClient(unittest.TestCase):
    def setUp(self):
        cli.VERBOSE = True
        self.start_date = datetime.now()
        ghclient = self.__create_mock_github()
        self.client = GHClient("fake-access-token", ghclient)
        self.assertTrue(self.client != None)

    @patch('github.Github')
    @patch('github.Organization')
    def __create_mock_github(self, MockGithub, MockOrganization):
        client = MockGithub()
        org = MockOrganization()
        org.name = 'fake-org'

        class FakeUser:
            def __init__(self, no):
                self.no = no
                self.login = "user{no}".format(no=no)
                self.created_at = datetime.now()

        class Fake:
            def __init__(self,no):
                self.no = no
                self.user = FakeUser(no)
                self.created_at = datetime.now()

        class FakeReview(Fake):
            def __init__(self, no):
                Fake.__init__(self, no)
                self.submitted_at = self.created_at

        class FakePullRequest(Fake):
            def __init__(self, no):
                Fake.__init__(self, no)

            def get_reviews(self):
                return [FakeReview(0), FakeReview(1), FakeReview(2)]

        class FakeIssue(Fake):
            def __init__(self, no):
                Fake.__init__(self, no)

        class FakeStatContributor(Fake):
            def __init__(self, no):
                Fake.__init__(self, no)
                self.author = self.user
                class FakeWeek:
                    def __init__(self):
                        self.w = datetime.now()
                        self.c = 1
                self.weeks = [FakeWeek(), FakeWeek(), FakeWeek()]

        class FakeRepo:
            def __init__(self, name):
                self.name = name

            def get_pulls(self, state='close'):
                return [FakePullRequest(0), FakePullRequest(1), FakePullRequest(2)]

            def get_issues(self, since=datetime.now(), state='close'):
                return [FakeIssue(0), FakeIssue(1), FakeIssue(2)]

            def get_stats_contributors(self):
                return [FakeStatContributor(0), FakeStatContributor(1), FakeStatContributor(2)]

        org.get_repos.return_value = [FakeRepo('fake-repo0'), FakeRepo('fake-repo1'), FakeRepo('fake-repo2')]
        client.get_organization.return_value = org
        return client

    def test_get_client(self):
        ghclient = self.client.get_client()
        self.assertTrue(ghclient != None)

    def test_repos(self):
        self.assertTrue(self.client.repos('fake-org') != None)
        self.assertTrue(len(self.client.repos('fake-org')) == 3)

    def test_reviews_count(self):
        fake_repo = self.client.repos('fake-org')[0]
        reviews_count = self.client.reviews_count(fake_repo, 'user0', self.start_date, datetime.now()+timedelta(days=1))
        self.assertTrue(reviews_count == 3)

    def test_prs_count(self):
        fake_repo = self.client.repos('fake-org')[0]
        prs_count = self.client.prs_count(fake_repo, 'user0', self.start_date, datetime.now()+timedelta(days=1))
        self.assertTrue(prs_count == 1)

    def test_issues_count(self):
        fake_repo = self.client.repos('fake-org')[0]
        issues_count = self.client.issues_count(fake_repo, 'user0', self.start_date, datetime.now()+timedelta(days=1))
        self.assertTrue(issues_count == 1)

    def test_commits_count(self):
        fake_repo = self.client.repos('fake-org')[0]
        commits_count = self.client.commits_count(fake_repo, 'user0', self.start_date, datetime.now()+timedelta(days=1))
        self.assertTrue(commits_count == 3)

if __name__ == '__main__':
    unittest.main()