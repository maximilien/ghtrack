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

  -s --state=closed              State one of 'open' or 'closed' [default: closed].

  --users=user1,user2,...        List of GitHub user IDs to track.

  --all-repos                    Track all repositories in GitHub organization.
  --repos=repo1,repo2,...        List of repositories in GitHub organization to track.
  --skip-repos=repo1,repo2,...   List of repositories in GitHub organization to skip.

  -a --access-token=ACCESS_TOKEN Your GitHub access token to access GitHub APIs.

  -o --output=CSV                The format of the output: text, json, yml, or csv [default: text].
  -f --output-file=output.csv    The file path to save results file.

  -h --help                      Show this screen.
  -v --version                   Show version."""

class GHT:
    def __init__(self, cmds):
        self.cmds = cmds
        self.out, self.err = "", ""

    def execute(self):
        try:
            access_token = parse_credentials_map('../.ghtrack.yml')['access_token']
            output = subprocess.check_output(["python3", "../ghtrack.py", "--access-token={access_token}".format(access_token=access_token)] + self.cmds)
            self.out = output.decode("utf-8").rstrip()
        except CalledProcessError as cpe:
            self.out = cpe.output
            return cpe.returncode
        return 0

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

#TODO: consolidate in common class TestBasicWorkflow 
# with 'text', 'json', 'yml' parameter
class TestBasicWorkflow_stdout(unittest.TestCase):
    def test_commits(self):
        cmd_line = "commits january knative --users=maximilien --repos=client --verbose"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("processing repos" in ght.out)
        self.assertTrue("OK" in ght.out)

    def test_reviews(self):
        cmd_line = "reviews january knative --users=maximilien,octocat --repos=client,client-contrib --verbose"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("processing repos" in ght.out)
        self.assertTrue("OK" in ght.out)

    def test_prs(self):
        cmd_line = "prs january knative --users=maximilien --repos=client --skip-repos=client-contrib --verbose"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("processing repos" in ght.out)
        self.assertTrue("OK" in ght.out)

    def test_issues(self):
        cmd_line = "issues january knative --users=maximilien,octocat --repos=client,client-contrib --skip-repos=client-contrib --verbose"
        cmd_line_args = cmd_line.split(" ")
        ght = GHT(cmd_line_args)
        rc = ght.execute()
        self.assertEqual(rc, 0)
        self.assertTrue("processing repos" in ght.out)
        self.assertTrue("OK" in ght.out)

class TestBasicWorkflow_json(unittest.TestCase):
    def test_commits(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "commits january knative -o json --output-file={tmp_file} --users=maximilien --repos=client".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_reviews(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "reviews january knative -o json --output-file={tmp_file} --users=maximilien,octocat --repos=client,client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_prs(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "prs january knative --output=json --output-file={tmp_file} --users=maximilien --repos=client --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_issues(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "issues january knative --output=JSON -f {tmp_file} --users=maximilien,octocat --repos=client,client-contrib --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

class TestBasicWorkflow_yml(unittest.TestCase):
    def test_commits(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "commits january knative -o yaml --output-file={tmp_file} --users=maximilien --repos=client".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_reviews(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "reviews january knative -o YAML --output-file={tmp_file} --users=maximilien,octocat --repos=client,client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_prs(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "prs january knative --output=YAML --output-file={tmp_file} --users=maximilien --repos=client --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_issues(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "issues january knative --output=yml -f {tmp_file} --users=maximilien,octocat --repos=client,client-contrib --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

class TestBasicWorkflow_csv(unittest.TestCase):
    def test_commits(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "commits january knative -o csv --output-file={tmp_file} --users=maximilien --repos=client".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_reviews(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "reviews january knative -o CSV --output-file={tmp_file} --users=maximilien,octocat --repos=client,client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_prs(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "prs january knative --output=CSV --output-file={tmp_file} --users=maximilien --repos=client --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)

    def test_issues(self):
        tmp_file, tmp_filepath = tempfile.mkstemp()
        cmd_line = "issues january knative --output=csv -f {tmp_file} --users=maximilien,octocat --repos=client,client-contrib --skip-repos=client-contrib".format(tmp_file=tmp_filepath)
        cmd_line_args = cmd_line.split(" ")
        try:
            ght = GHT(cmd_line_args)
            rc = ght.execute()
            self.assertEqual(rc, 0)
            self.assertTrue("OK" in ght.out)
        finally:
            os.remove(tmp_filepath)
