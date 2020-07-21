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

import yaml, csv, os.path

from client import GHClient

VERBOSE=False

class Console:
    def print(msg):
        if VERBOSE:
            print(msg)

class Credentials:
    def __init__(self, hash):
        self.hash = hash

    def access_token(self):
        return self.hash['access_token']

class CLI:
    def __init__(self, args):
        self.args = args
        self.credentials = self.__setup_credentials()
        if self.args['--verbose']:
            VERBOSE = True

    def __parse_credentials(self):
        credentials_hash = {'access_token': ''}
        file_name = '.ghtrack.yml'
        if '--credentials' in self.args: file_name = self.args['--credentials']
        try:
            with open(file_name) as file:
                loaded_credentials = yaml.load(file, Loader=yaml.FullLoader)
                credentials_hash.update(loaded_credentials)
        except:
            Console.print("Error opening credentials file: {file_name}".format(file_name=file_name))
        return credentials_hash

    def __setup_credentials(self):
        credentials_hash = self.__parse_credentials()
        if self.args['--access-token'] and self.args['--credentials']:
            Console.print("WARNING: using --access-token value in credentials")
            credentials_hash['access_token'] = self.args['--access-token']
        else:
            self.args['--access-token'] = credentials_hash['access_token']
        return Credentials(credentials_hash)

    def command(self, client=None):
        if client == None:
            client = GHClient(self.credentials)

        if self.args.get('commits') and self.args['commits']:
            return Commits(self.args, self.credentials, client)
        elif self.args.get('reviews') and self.args['reviews']:
            return Reviews(self.args, self.credentials, client)
        elif self.args.get('issues') and self.args['issues']:
            return Issues(self.args, self.credentials, client)
        elif self.args.get('stats') and self.args['stats']:
            return Stats(self.args, self.credentials, client)
        else:
            raise Exception("Invalid command")

class Command:
    LIST_OPTIONS = ['--users', '--repos', '--skip-repos']
    def __init__(self, args, credentials, client):
        self.__init_empty_options(args)
        self.args = args
        self.credentials = credentials
        self.client = client

    def __init_empty_options(self, args):
        for option in self.LIST_OPTIONS:
            if args[option] == None:
                args[option] = []
            elif isinstance(args[option], str):
                args[option] = [args[option]]

    def println(self, msg):
        self.print(msg + "\n")

    def print(self, msg):
        #TODO: check for file output
        print(msg)

    def verbose(self):
        return self.args['--verbose']

    def month(self):
        return self.args['MONTH']

    def users(self):
        return self.args['--users']

    def org(self):
        return self.args['--org']

    def repos(self):
        return self.args['--repos']

    def skip_repos(self):
        return self.args['--skip-repos']

    def all_repos(self):

        return self.args['--all-repos']

    def cmd_line(self):
        repos_line = "--all-repos"
        if self.args['--all-repos'] == False:
            repos_line = "--repos={repos} --skip-repos={skip_repos}".format(repos=','.join(self.repos()), skip_repos=','.join(self.skip_repos()))
        cmd_line = "{name} {month} --users={users} --org={org}".format(name=self.name(), month=self.month(), users=','.join(self.users()), org=self.org())
        cmd_line += " " + repos_line
        return cmd_line

    def start_comment(self):
        print("# GH Track output for cmd line: {cmd_line}".format(cmd_line=self.cmd_line()))

    def execute(self):
        func = self.dispatch()
        rc = func()
        if rc == None:
            return 0
        else:
            if isinstance(rc, int):
                return rc
            else:
                return -1

    def dispatch(self):
        if self.args['commits']:
            return self.commits
        elif self.args['reviews']:
            return self.reviews
        elif self.args['issues']:
            return self.issues
        elif self.args['stats']:
            return self.stats
        else:
            raise Exception("Invalid subcommand")

# commits command group
class Commits(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        super().__init__(self.args, credentials, client)

    def __print(self, commit):
        print("Commits: {args}".format(args=self.args))

    def name(self):
      return "commits"

    def commits(self):
        self.start_comment()
        return 0

# reviews command group
class Reviews(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        super().__init__(self.args, credentials, client)

    def __print(self, commit):
        print("Reviews: {args}".format(args=self.args))

    def name(self):
      return "reviews"

    def reviews(self): 
        self.start_comment()
        return 0

# issues command group
class Issues(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        super().__init__(self.args, credentials, client)

    def __print(self, commit):
        print("Issues: {args}".format(args=self.args))

    def name(self):
      return "issues"

    def issues(self):
        self.start_comment()
        return 0

# stats command group
class Stats(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        super().__init__(self.args, credentials, client)

    def __print(self, commit):
        print("Stats: {args}".format(args=self.args))

    def name(self):
      return "stats"

    def stats(self):
        self.start_comment()
        return 0
