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
  -v --version                   Show version.

"""
import os, sys, traceback

from docopt import docopt
from cli import *

if __name__ == '__main__':
    args = docopt(__doc__, version='GH Track v0.3.5.3')
    command = CLI(args).command()
    rc = command.execute()
    if rc != 0:
        Console.error("executing command: {rc}".format(rc=rc))
        sys.exit(rc)
