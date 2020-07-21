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

import os, sys, subprocess, unittest

HELP_STRING = """GitHub track

Usage:
  ght commits MONTH ORG [options]
  ght reviews MONTH ORG [options]
  ght issues MONTH ORG [options]
  ght stats MONTH ORG [options]

  ght (-h | --help)
  ght (-v | --version)

Options:
  --verbose                      Show all output.

  --commits                      Collect commits stats.
  --reviews                      Collect reviews stats.
  --issues                       Collect issues stats.

  --users=user1,user2,...        List of GitHub user IDs to track.

  --all-repos                    Track all repositories in GitHub organization.
  --repos=repo1,repo2,...        List of repositories in GitHub organization to track.
  --skip-repos=repo1,repo2,...   List of repositories in GitHub organization to skip.

  -a --access-token=ACCESS_TOKEN Your GitHub access token to access GitHub APIs.
  -o --output=FILE               The file path to save results CSV file.

  -h --help                      Show this screen.
  -v --version                   Show version."""

class GHT:
    def __init__(self, cmds):
        self.cmds = cmds
        self.out, self.err = "", ""

    def execute(self):
        try:
            output = subprocess.check_output(["python3", "../ghtrack.py"] + self.cmds)
            self.out = output.decode("utf-8").rstrip()
        except CalledProcessError as cpe:
            self.out = cpe.output
            return cpe.returncode
        return 0

class TestBasicWorkflow_stdout(unittest.TestCase):
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

    def test_commits(self):
        cmd_line = "commits january knative --users=maximilien --repos=client"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("# GH Track output for cmd line: {cmd_line}".format(cmd_line=cmd_line) in ght.out)

    def _test_reviews(self):
        cmd_line = "reviews january knative --users=maximilien --repos=client"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("# GH Track output for cmd line: {cmd_line}".format(cmd_line=cmd_line) in ght.out)

    def _test_issues(self):
        cmd_line = "issues january knative --users=maximilien --repos=client"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("# GH Track output for cmd line: {cmd_line}".format(cmd_line=cmd_line) in ght.out)

    def _test_stats(self):
        cmd_line = "stats january knative --commits --reviews --issues --users=maximilien --repos=client"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("# GH Track output for cmd line: {cmd_line}".format(cmd_line=cmd_line) in ght.out)

class TestBasicWorkflow_csv(unittest.TestCase):
    pass

class TestAdvancedWorkflow_csv(unittest.TestCase):
    pass