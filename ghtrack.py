#!/usr/bin/env python3

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

"""GitHub track

Usage:
  ght commits MONTH [options]
  ght reviews MONTH [options]
  ght issues MONTH [options]
  ght stats MONTH [options]

  ght (-h | --help)
  ght (-v | --version)

Options:
  --verbose                      Show all output.

  --commits                      Collect commits stats.
  --reviews                      Collect reviews stats.
  --issues                       Collect issues stats.

  --users=user1,user2,...        List of GitHub user IDs to track.
  --org=organization             The GitHub organization.

  --all-repos                    Track all repositories in GitHub organization.
  --repos=repo1,repo2,...        List of repositories in GitHub organization to track.
  --skip-repos=repo1,repo2,...   List of repositories in GitHub organization to skip.

  -a --access-token=ACCESS_TOKEN Your GitHub access token to access GitHub APIs.
  -o --output=FILE               The file path to save results CSV file.

  -h --help                      Show this screen.
  -v --version                   Show version.

"""
import os, sys, traceback

from docopt import docopt
from cli import *

if __name__ == '__main__':
    args = docopt(__doc__, version='GH Track v0.0')
    command = CLI(args).command()
    rc = command.execute()
    if rc != 0:
        sys.exit(rc)
