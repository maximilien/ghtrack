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
from client import *

class TestGHClient(unittest.TestCase):
    def setUp(self):
        cli.VERBOSE = True
        self.client = GHClient("fake-access-token")
        self.assertTrue(self.client != None)

    @patch('github.Github')
    def __create_mock_github(self, MockGithub):
        return MockGithub()

    def test_get_client(self):
        ghclient = self.client.get_client()
        self.assertTrue(self.client != None)

    def test_repos(self):
        pass

    def test_commits_count(self):
        pass

    def test_reviews_count(self):
        pass

    def test_prs_count(self):
        pass

    def test_issues_count(self):
        pass

if __name__ == '__main__':
    unittest.main()