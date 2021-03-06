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

import os, sys, subprocess, unittest, tempfile

sys.path.insert(0, "{current_dir}/..".format(current_dir=os. getcwd()))

from cli import parse_credentials_map

HELP_STRING = """GitHub track

Usage:
  ght commits MONTH ORG [options]
  ght prs MONTH ORG [options]
  ght reviews MONTH ORG [options]
  ght issues MONTH ORG [options]
  ght stats MONTH ORG [options]

  ght (-h | --help)
  ght (-v | --version)

Options:
  --verbose                      Show all output.

  --commits                      Collect commits stats.
  --prs                          Collect PRs stats.
  --reviews                      Collect reviews stats.
  --issues                       Collect issues stats.

  --summarize                    Summarize collected stats.

  --rate-limit                   Enables rate limiting (default or speficy --rl-* options).
  --rate-limit-random            Enables rate limiting by randomly picking max and sleep value with default or --rl-* values as ceilings.
  --rl-max=100                   Max number of API calls before sleeping [default: 100].
  --rl-sleep=30m                 Time to sleep once max API calls reach, e.g., 30m, 1h for 30 mins, 1 hour [default: 30m].

  -s --state=closed              State one of 'open' or 'closed' [default: closed].

  --users=user1,user2,...        List of GitHub user IDs to track.

  --all-repos                    Track all repositories in GitHub organization.
  --repos=repo1,repo2,...        List of repositories in GitHub organization to track.
  --skip-repos=repo1,repo2,...   List of repositories in GitHub organization to skip.
  --show-all-stats               Show all stats even when 0 or non-existant for a user [default: False].

  -a --access-token=ACCESS_TOKEN Your GitHub access token to access GitHub APIs.

  -o --output=CSV                The format of the output: text, json, yml, or csv [default: text].
  -f --file=output.csv           The file path to save results file.

  -h --help                      Show this screen.
  -v --version                   Show version."""

class GHT:
    def __init__(self, cmds):
        self.cmds = cmds
        self.out, self.err = "", ""

    def execute(self):
        try:
            access_token = os.getenv('GH_ACCESS_TOKEN', '')
            if access_token == '':
                access_token = parse_credentials_map('../.ghtrack.yml')['gh_access_token']
            output = subprocess.check_output(["python3", "../ghtrack.py", "--access-token={access_token}".format(access_token=access_token)] + self.cmds)
            self.out = output.decode("utf-8").rstrip()
        except Exception as e:
            self.out = e.output
            return e.returncode
        return 0

class BasicWorkflow:
    def __init__(self, output):
        self.output = output
        self.tc = unittest.TestCase()

    def _test_stats_commits_prs(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "stats june knative --commits --prs --output={output} -f {tmp_file} --users=maximilien,octocat --repos=client,client-contrib".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def _test_stats_prs_issues(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "stats july knative --prs --issues --o {output} --file={tmp_file} --users=octocat --repos=client,client-contrib".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_stats(self):
        self._test_stats_prs_issues()
        self._test_stats_commits_prs()

    def test_commits(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "commits january knative -o {output} --file={tmp_file} --users=maximilien --repos=client".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_reviews(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "reviews january knative -o {output} --file={tmp_file} --users=maximilien --repos=client-contrib".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_prs(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "prs january knative --output={output} --file={tmp_file} --users=maximilien --repos=client --skip-repos=client-contrib".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_issues(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "issues january knative --output={output} -f {tmp_file} --users=maximilien,octocat --repos=client,client-contrib --skip-repos=client-contrib".format(output=self.output, tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.tc.assertEqual(rc, 0)
            self.tc.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

class TestCommonWorkflow_stdout(unittest.TestCase):
    def test_help(self):
        ght = GHT(["--help"])
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertEqual(HELP_STRING, ght.out)

    def test_version(self):
        ght = GHT(["--version"])
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("GH Track v" in ght.out)

class TestBasicWorkflow(unittest.TestCase):
    def test_commits(self):
        BasicWorkflow('json').test_commits()

    def test_reviews(self):
        BasicWorkflow('yml').test_reviews()

    def test_prs(self):
        BasicWorkflow('csv').test_prs()

    def test_issues(self):
        BasicWorkflow('text').test_issues()

    def test_stats(self):
        BasicWorkflow('text').test_stats()
