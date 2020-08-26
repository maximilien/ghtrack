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

import io, sys, yaml, json, csv, os.path

from datetime import datetime
from calendar import monthrange
from tabulate import tabulate

from client import GHClient

from common import *

def parse_credentials_map(file_name):
    credentials_map = {'gh_access_token': ''}
    try:
        with open(file_name) as file:
            loaded_credentials = yaml.load(file, Loader=yaml.FullLoader)
            credentials_map.update(loaded_credentials)
    except:
        if VERBOSE:
            Console.warn("opening credentials file: {file_name}".format(file_name=file_name))
    return credentials_map

class Credentials:
    def __init__(self, hash):
        self.hash = hash

    def __gh_access_token_from_environment(self):
        return os.getenv('GH_ACCESS_TOKEN', '')

    def access_token(self):
        access_token = self.__gh_access_token_from_environment()
        if access_token == '' or access_token == None:
            access_token = self.hash['gh_access_token']
        return access_token

class CLI:
    def __init__(self, args):
        self.args = args
        self.credentials = self.__setup_credentials()
        if self.args['--verbose']:
            VERBOSE = True

    def __parse_credentials(self):
        file_name = '.ghtrack.yml'
        if '--credentials' in self.args: file_name = self.args['--credentials']
        return parse_credentials_map(file_name)

    def __setup_credentials(self):
        credentials_hash = self.__parse_credentials()
        if self.args['--access-token']:
            credentials_hash['gh_access_token'] = self.args['--access-token']
        else:
            self.args['--access-token'] = credentials_hash['gh_access_token']
        return Credentials(credentials_hash)

    def command(self, client=None):
        if client == None:
            client = GHClient(self.credentials.access_token())
        if self.args.get('commits') and self.args['commits']:
            return Commits(self.args, self.credentials, client)
        elif self.args.get('reviews') and self.args['reviews']:
            return Reviews(self.args, self.credentials, client)
        elif self.args.get('prs') and self.args['prs']:
            return PRs(self.args, self.credentials, client)
        elif self.args.get('issues') and self.args['issues']:
            return Issues(self.args, self.credentials, client)
        elif self.args.get('stats') and self.args['stats']:
            return Stats(self.args, self.credentials, client)
        else:
            raise Exception("Invalid command")

class Command:
    BOOL_OPTIONS = ['--summarize']
    LIST_OPTIONS = ['--users', '--repos', '--skip-repos']
    MONTHS_CAP = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    MONTHS_LOWER = {'january':1, 'february':2, 'march':3, 'april':4, 'may':5, 'june':6, 'july':7, 'august':8, 'september':9, 'october':10, 'november':11, 'december':12}
    MONTHS_UPPER = {'JANUARY':1, 'FEBRUARY':2, 'MARCH':3, 'APRIL':4, 'MAY':5, 'JUNE':6, 'JULY':7, 'AUGUST':7, 'SEPTEMBER':9, 'OCTOBER':10, 'NOVEMBER':11, 'DECEMBER':12}
    MONTHS_ABREV = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
    OUTPUT_JSON = ['json', 'jsn', 'JSON', 'JSN']
    OUTPUT_YAML = ['yaml', 'yml', 'YAML', 'YML']
    OUTPUT_CSV = ['csv', 'CSV']
    SECONDS_MULIPLIER = {'s':1, 'm':60, 'h':3600, 'd':24*3600}
    def __init__(self, args, credentials, client):
        self.__init_empty_options(args)
        self.args = args
        self.credentials = credentials
        self.client = client
        self.repos_stats = self._init_repos_stats()
        self.summary_stats = self._init_summary_stats()
        self.rate_limit_data = self._init_rate_limit_data()
        self.client.set_rate_limit_data(self.rate_limit_data)
        self.__month_number = 0

    def __init_empty_options(self, args):
        for option in self.BOOL_OPTIONS:
            if args[option] == None:
                args[option] = False
        for option in self.LIST_OPTIONS:
            if args[option] == None or args[option] == '':
                args[option] = []
            elif isinstance(args[option], str):
                if ',' in args[option]:
                    args[option] = args[option].split(',')
                else:
                    args[option] = [args[option]]

    def _init_request(self, map, data_name):
        map['request'] = {}
        map['request']['org'] = self.org()
        map['request']['state'] = self.state()
        map['request']['year'] = self.year()
        map['request']['month'] = self.month()
        map['request']['data'] = data_name

    def _init_users_stats(self, users_stats):
        for user in self.users():
            users_stats[user] = {}
            for repo in self.repos():
                if repo not in self.skip_repos():
                    users_stats[user][repo] = 0

    def _init_repos_stats(self):
        repo_stats = {} #{'repo_name': {'commits': 0, 'prs': 0, 'reviews': 0, 'issues': 0},  ...}
        for repo in self.repos():
            if repo not in self.skip_repos():
                repo_stats[repo] = {}
                repo_stats[repo]['commits'] = 0
                repo_stats[repo]['prs'] = 0
                repo_stats[repo]['reviews'] = 0
                repo_stats[repo]['issues'] = 0
        return repo_stats

    def _init_summary_stats(self):
        data = ['commits', 'prs', 'issues', 'reviews']
        summary_stats = {} #{'commits': {'repo0': 0, 'repo1': 0, ...},{'reviews': {'repo0': 0, ...},...}
        for repo in self.repos():
            if repo not in self.skip_repos():
                for item in data:
                    summary_stats[item] = {repo: 0}
        return summary_stats

    def _init_rate_limit_data(self):
        if not self.rate_limit():
            return RateLimitData(0, 0, False)

        rate_limit_data = RateLimitData(RateLimitData.DEFAULT_RATE_LIMIT_MAX, RateLimitData.DEFAULT_RATE_LIMIT_SLEEP, True)
        if not self.check_rl_max():
            Console.print("Using default rate limit API calls of '{default}'".format(default=RateLimitData.DEFAULT_RATE_LIMIT_MAX))
        else:
            rate_limit_data.max_calls = self.rl_max()

        if not self.check_rl_sleep():
            Console.print("Using default rate limit sleep of '{default}'".format(default=RateLimitData.DEFAULT_RATE_LIMIT_SLEEP))
        else:
            rate_limit_data.sleep = self._parse_rl_sleep()

        return rate_limit_data

    # returns --rl-sleep value in seconds, so 1h == 3600
    def _parse_rl_sleep(self):
        sleep_seconds = 0
        rl_sleep = self.rl_sleep()
        try:
            unit = rl_sleep[len(rl_sleep)-1:]
            value = int(rl_sleep[0:len(rl_sleep)-1])
            sleep_seconds = self.SECONDS_MULIPLIER[unit.lower()]*value
        except:
            Console.warn("Error parsing --rl-sleep value '{rl_sleep}".format(rl_sleep=self.rl_sleep()))
        return sleep_seconds

    def _write_map_as_csv(self, output_stream, output_map):
        writer = csv.DictWriter(output_stream, output_map.keys())
        writer.writeheader()
        writer.writerow(output_map)

    def _write_list_as_csv(self, output_stream, output_list):
        writer = csv.writer(output_stream)
        for item in output_list:
            writer.writerow(item)

    def _extract_user_repo_data(self, request_data, users_repos_map):
        users_repos_data = []
        data_headers = ['user', 'repo', 'data', 'count']
        users_repos_data.append(data_headers)
        for user in self.users():
            for repo in self.repos():
                if repo not in self.skip_repos():
                    users_repos_data_count = 0
                    if repo in users_repos_map[user]:
                        users_repos_data_count = users_repos_map[user][repo]
                        if users_repos_data_count == 0 and not self.show_all_stats():
                            continue
                        users_repos_data.append([user, repo, request_data, users_repos_data_count])
        return users_repos_data

    def _extract_repos_stats_table(self):
        header = ['repo', 'data', 'total']
        table = []
        for repo in self.repos():
            if repo not in self.skip_repos():
                repo_stats = self.repos_stats[repo]
                for item in repo_stats:
                    row = [repo, item, repo_stats[item]]
                    table.append(row)
        return (header, table)

    def _extract_summary_stats_table(self):
        header = ['data', 'repo', 'total']
        table = []
        for data in self.summary_stats.keys():
            data_stats = self.summary_stats[data]
            for repo in self.repos():
                if repo not in self.skip_repos():
                    for item in data_stats:
                        row = [data, repo, data_stats[item]]
                        table.append(row)
        return (header, table)

    def _print_summarize_output(self):
        if self.output() in self.OUTPUT_JSON:
            self._print_output_json(self.repos_stats)
            self._print_output_json(self.summary_stats)
        elif self.output() in self.OUTPUT_YAML:
            self._print_output_yml(self.repos_stats)
            self._print_output_yml(self.summary_stats)
        elif self.output() in self.OUTPUT_CSV:
            self._print_summarize_output_cvs()
        else:
            self._print_summarize_output_text()
        Console.println()

    def _print_summarize_output_text(self):
        Console.println(2)
        header, table = self._extract_repos_stats_table()
        print(tabulate(table, headers=header))
        Console.println()
        header, table = self._extract_summary_stats_table()
        print(tabulate(table, headers=header))

    def _print_summarize_output_cvs(self):
        Console.println()
        repos_stats_headers = ['repo', 'data', 'total']
        with open(self.file(), 'a', newline='') as csv_file:
            csv_file.write('\n')
            header, repos_stats_table = self._extract_repos_stats_table()
            self._write_list_as_csv(csv_file, [header, *repos_stats_table])
            csv_file.write('\n')
            header, summary_stats_table = self._extract_summary_stats_table()
            self._write_list_as_csv(csv_file, [header, *summary_stats_table])

    def _print_output_text(self, output_map):        
        Console.println()
        request_headers = ['org', 'year', 'month', 'data', 'state']
        r = output_map['request']
        print(tabulate([[r['org'], r['year'], r['month'], r['data'], r['state']]], headers=request_headers))
        
        Console.println()
        users_repos_data = self._extract_user_repo_data(output_map['request']['data'], output_map)
        print(tabulate(users_repos_data[1:], headers=users_repos_data[0]))
        Console.println()

    def _print_output_json(self, output_map):
        Console.println()
        text_output = json.dumps(output_map, indent=4, sort_keys=True)
        if self.file() == None or self.file() == '':
            Console.print(text_output)
        else:
            with open(self.file(), 'a') as json_file:
                json_file.write('\n')
                json_file.write(text_output)

    def _print_output_yml(self, output_map):
        Console.println()
        if self.file() == None or self.file() == '':
            Console.print(yaml.dump(output_map))
        else:
            with open(self.file(), 'a') as yml_file:
                yml_file.write('\n')
                yaml.dump(output_map, yml_file, default_flow_style=False)

    def _print_output_csv(self, output_map):
        request_map = output_map['request']
        Console.println()
        if self.file() == None or self.file() == '':
            output_stream = io.StringIO()
            self._write_map_as_csv(output_stream, request_map)
            users_repos_data = self._extract_user_repo_data(output_map['request']['data'], output_map)
            self._write_list_as_csv(output_stream, users_repos_data)
            Console.print(output_stream.getvalue())
        else:
            with open(self.file(), 'a', newline='') as csv_file:
                csv_file.write('\n')
                self._write_map_as_csv(csv_file, request_map)
                csv_file.write('\n')
                users_repos_data = self._extract_user_repo_data(output_map['request']['data'], output_map)
                self._write_list_as_csv(csv_file, users_repos_data)

    # data is one of 'commits', 'prs', 'reviews', 'issues'
    # data_map is map {'user0': {'repo0': count0, 'repo1': count1, ...}, {...}}
    # output: {'repo0': {'commits': total0, 'issues': total1, ...}, {...}}
    def _update_repo_stats(self, data, data_map):
        for user in self.users():
            user_data_map = data_map[user]
            for repo_name in user_data_map:
                self.repos_stats[repo_name][data] += user_data_map[repo_name]

    # data is one of 'commits', 'prs', 'reviews', 'issues'
    # data_map is map {'user0': {'repo0': count0, 'repo1': count1, ...}, {...}}
    # output: {'commits': {'repo0': total0, 'repo1': total1, ...}, {...}}
    def _update_summary_stats(self, data, data_map):
        for user in self.users():
            user_data_map = data_map[user]
            for repo_name in user_data_map:
                if repo_name in self.summary_stats[data]:
                    self.summary_stats[data][repo_name] += user_data_map[repo_name]
                else:
                    self.summary_stats[data][repo_name] = user_data_map[repo_name]

    def _update_users_issues(self):
        repos = self.client.repos(self.org())
        totalReposCount = repos.totalCount
        for user in self.users():
            Console.print("Getting 'issues' for '{user}' in organization: '{org}'".format(user=user, org=self.org()))
            count = 1
            for repo in repos:
                Console.progress(count, totalReposCount, status="processing repos".format(name=repo.name))
                if repo.name in self.repos() and repo.name not in self.skip_repos():
                    issues_count = self.client.issues_count(repo, user, self.start_date(), self.end_date(), self.state())
                    if issues_count == 0 and not self.show_all_stats():
                            continue
                    self.users_issues[user][repo.name] = issues_count
                count += 1
            Console.println()
        self._update_repo_stats('issues', self.users_issues)
        self._update_summary_stats('issues', self.users_issues)

    def _update_users_prs(self):
        repos = self.client.repos(self.org())
        for user in self.users():
            totalReposCount = repos.totalCount
            Console.print("Getting 'prs' for '{user}' in organization: '{org}'".format(user=user, org=self.org()))
            count = 1
            for repo in repos:
                Console.progress(count, totalReposCount, status="processing repos".format(name=repo.name))
                if repo.name in self.repos() and repo.name not in self.skip_repos():
                    prs_count = self.client.prs_count(repo, user, self.start_date(), self.end_date(), self.state())
                    if prs_count == 0 and not self.show_all_stats():
                            continue
                    self.users_prs[user][repo.name] = prs_count
                count += 1
            Console.println()
        self._update_repo_stats('prs', self.users_prs)
        self._update_summary_stats('prs', self.users_prs)

    def _update_users_reviews(self):
        repos = self.client.repos(self.org())
        totalReposCount = repos.totalCount
        for user in self.users():
            Console.print("Getting 'reviews' for '{user}' in organization: '{org}'".format(user=user, org=self.org()))
            count = 1
            for repo in repos:
                Console.progress(count, totalReposCount, status="processing repos".format(name=repo.name))
                if repo.name in self.repos() and repo.name not in self.skip_repos():
                    reviews_count = self.client.reviews_count(repo, user, self.start_date(), self.end_date())
                    if reviews_count == 0 and not self.show_all_stats():
                            continue
                    self.users_reviews[user][repo.name] = reviews_count
                count += 1
            Console.println()
        self._update_repo_stats('reviews', self.users_reviews)
        self._update_summary_stats('reviews', self.users_reviews)

    def _update_users_commits(self):
        repos = self.client.repos(self.org())
        totalReposCount = repos.totalCount
        for user in self.users():
            Console.print("Getting 'commits' for '{user}' in organization: '{org}'".format(user=user, org=self.org()))
            count = 1
            for repo in repos:
                Console.progress(count, totalReposCount, status="processing repos".format(name=repo.name))
                if repo.name in self.repos() and repo.name not in self.skip_repos():
                    commits_count = self.client.commits_count(repo, user, self.start_date(), self.end_date())
                    if commits_count == 0 and not self.show_all_stats():
                            continue
                    self.users_commits[user][repo.name] = commits_count
                count += 1
            Console.println()
        self._update_repo_stats('commits', self.users_commits)
        self._update_summary_stats('commits', self.users_commits)

    def check_month(self, month):
        if month in self.MONTHS_LOWER.keys():
            self.__month_number = self.MONTHS_LOWER[month]
            return True
        elif month in self.MONTHS_UPPER.keys():
            self.__month_number = self.MONTHS_UPPER[month]
            return True
        elif month in self.MONTHS_CAP.keys():
            self.__month_number = self.MONTHS_CAP[month]
            return True
        elif month in self.MONTHS_ABREV.keys():
            self.__month_number = self.MONTHS_ABREV[month]
            return True
        return False

    def check_org(self, org):
        if org == None:
            return False
        elif org == '':
            return False
        return True

    def check_state(self, state):
        if state == 'closed':
            return True
        elif state == 'open':
            return True
        return False

    def check_credentials(self):
        if self.credentials == None:
            Console.warn("Invalid credentials '{credentials}'".format(credentials=self.credentials))
            return False
        elif self.credentials.access_token() == '' or self.credentials.access_token() == None:
            Console.warn("Invalid credentials Github access token '{access_token}'".format(access_token=self.credentials.access_token()))
            return False
        return True

    def check_required_options(self):
        if not self.check_month(self.month()):
            Console.warn("Invalid month '{month}'".format(month=self.month()))
            return False
        elif not self.check_org(self.org()):
            Console.warn("Invalid org value '{org}'".format(org=self.org()))
            return False
        elif not self.check_state(self.state()):
            Console.warn("Invalid state value '{state}'".format(state=self.state()))
            return False
        return True

    def check_rl_max(self):
        if '--rl-max' not in self.args:
            return False
        if self.rl_max() < 0:
            Console.warn("Invalid --rl-max value '{rl_max}'".format(rl_max=self.rl_max()))
            return False
        return True

    def check_rl_sleep(self):
        if '--rl-sleep' not in self.args:
            return False
        if self.rl_sleep().__class__ != ''.__class__:
            return False
        if self.rl_sleep() == '':
            return False
        sleep_seconds = self._parse_rl_sleep()
        if sleep_seconds <= 0:
            Console.warn("Invalid --rl-sleep value '{rl_sleep}'".format(rl_sleep=self.rl_sleep()))
            return False
        return True

    def println(self, msg):
        self.print(msg + "\n")

    def print(self, msg):
        Console.print(msg)

    def warn(self, msg):
        Console.warn(msg)

    def verbose(self):
        return self.args['--verbose']

    def state(self):
        return self.args['--state']

    def year(self):
        return datetime.now().year

    def start_date(self):
        return datetime(month=self.month_number(), day=1, year=self.year())

    def end_date(self):
        return datetime(month=self.month_number(), day=self.month_last_day(), year=self.year())

    def month_last_day(self):
        range = monthrange(self.year(), self.month_number())
        return range[1]

    def month_number(self):
        if self.__month_number == 0:
            checked = self.check_month(self.month())
            if not checked: Console.warn("month value: '{month}' is not valid".format(month=self.month()))
        return self.__month_number

    def month(self):
        return self.args['MONTH']

    def users(self):
        return self.args['--users']

    def org(self):
        return self.args['ORG']

    def repos(self):
        return self.args['--repos']

    def skip_repos(self):
        return self.args['--skip-repos']

    def all_repos(self):
        return self.args['--all-repos']

    def output(self):
        return self.args['--output']

    def file(self):
        return self.args['--file']

    def stats_commits(self):
        return self.args['--commits']

    def stats_reviews(self):
        return self.args['--reviews']

    def stats_prs(self):
        return self.args['--prs']

    def stats_issues(self):
        return self.args['--issues']

    def show_all_stats(self):
        return self.args['--show-all-stats']

    def summarize(self):
        return self.args['--summarize']

    def rate_limit(self):
        return self.args['--rate-limit']

    def rl_max(self):
        return self.args['--rl-max']

    def rl_sleep(self):
        return self.args['--rl-sleep']

    def cmd_line(self):
        repos_line = "--all-repos"
        if self.args['--all-repos'] == False:
            repos_line = "--repos={repos} --skip-repos={skip_repos}".format(repos=','.join(self.repos()), skip_repos=','.join(self.skip_repos()))
        cmd_line = "{name} {month} {org} --users={users}".format(name=self.name(), month=self.month(), users=','.join(self.users()), org=self.org())
        cmd_line += " " + repos_line
        return cmd_line

    def start_comment(self):
        Console.verbose("# GH Track output for cmd line: {cmd_line}".format(cmd_line=self.cmd_line()))

    def end_comment(self):
        if self.file() != None:
            Console.print("wrote output file: {file}".format(file=self.file()))

        if not self.show_all_stats():
            Console.print("Showing only non-zero stats, use --show-all-stats to view all")
        Console.ok("OK")

    def fetch_repos(self):
        if not self.all_repos(): return
        if self.all_repos() and len(self.repos()) > 0:
            self.warn("ignoring --repos since --all-repos is set")
        repo_names = []
        repos = self.client.repos(self.org())
        for repo in repos: repo_names.append(repo.name)
        self.args['--repos'] = repo_names

    def print_output(self, output_map):
        if self.output() in self.OUTPUT_JSON:
            self._print_output_json(output_map)
        elif self.output() in self.OUTPUT_YAML:
            self._print_output_yml(output_map)
        elif self.output() in self.OUTPUT_CSV:
            self._print_output_csv(output_map)
        else:
            self._print_output_text(output_map)
        if self.summarize() and self.name() != 'stats':
            self._print_summarize_output()

    def execute(self):
        self.fetch_repos()
        if not self.check_credentials():
            return 1
        elif not self.check_required_options():
            return 1
        func = self.dispatch()
        rc = func()
        if rc == None:
            return 0
        else:
            if isinstance(rc, int):
                return rc
            else:
                return 1

    def dispatch(self):
        if self.args['commits']:
            return self.commits
        elif self.args['reviews']:
            return self.reviews
        elif self.args['prs']:
            return self.prs
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
        self.users_commits = {} # {user: {repo_name: commit_count},...}
        super().__init__(self.args, credentials, client)
        self._init_request(self.users_commits, self.name())
        self._init_users_stats(self.users_commits)

    def name(self):
      return "commits"

    def commits(self):
        self.start_comment()
        Console.print("Getting commits for {total_users} users in {total_repos} repos via GitHub APIs... be patient".format(total_users=len(self.users()), total_repos=len(self.repos())))
        self._update_users_commits()
        self.print_output(self.users_commits)
        self.end_comment()
        return 0

# reviews command group
class Reviews(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        self.users_reviews = {} # {user: {repo_name: review_count},...}
        super().__init__(self.args, credentials, client)
        self._init_request(self.users_reviews, self.name())
        self._init_users_stats(self.users_reviews)

    def name(self):
      return "reviews"

    def reviews(self): 
        self.start_comment()
        Console.print("Getting reviews for {total_users} users in {total_repos} repos via GitHub APIs... be patient".format(total_users=len(self.users()), total_repos=len(self.repos())))
        self._update_users_reviews()
        self.print_output(self.users_reviews)
        self.end_comment()
        return 0

# prs command group
class PRs(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        self.users_prs = {} # {user: {repo_name: pr_count},...}
        super().__init__(self.args, credentials, client)
        self._init_request(self.users_prs, self.name())
        self._init_users_stats(self.users_prs)

    def name(self):
      return "prs"

    def prs(self):
        self.start_comment()
        Console.print("Getting prs for {total_users} users in {total_repos} repos via GitHub APIs... be patient".format(total_users=len(self.users()), total_repos=len(self.repos())))
        self._update_users_prs()
        self.print_output(self.users_prs)
        self.end_comment()
        return 0

# issues command group
class Issues(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        self.users_issues = {} # {user: {repo_name: issue_count},...}
        super().__init__(self.args, credentials, client)
        self._init_request(self.users_issues, self.name())
        self._init_users_stats(self.users_issues)

    def name(self):
      return "issues"

    def issues(self):
        self.start_comment()
        Console.print("Getting issues for {total_users} users in {total_repos} repos via GitHub APIs... be patient".format(total_users=len(self.users()), total_repos=len(self.repos())))
        self._update_users_issues()
        self.print_output(self.users_issues)
        self.end_comment()
        return 0

# stats command group
class Stats(Command):
    def __init__(self, args, credentials, client):
        self.args = args
        self.users_commits = {} # {user: {repo_name: commit_count},...}
        self.users_prs = {}     # {user: {repo_name: pr_count},...}
        self.users_issues = {}  # {user: {repo_name: issue_count},...}
        self.users_reviews = {} # {user: {repo_name: review_count},...}
        super().__init__(self.args, credentials, client)
        for data_tuple in [('commits', self.users_commits),
                           ('prs', self.users_prs),
                           ('issues', self.users_issues),
                           ('reviews', self.users_reviews)]:
            self._init_request(data_tuple[1], data_tuple[0])
            self._init_users_stats(data_tuple[1])

    def print_stats_output(self):
        if self.stats_commits():
            self.print_output(self.users_commits)
        if self.stats_prs():
            self.print_output(self.users_prs)
        if self.stats_reviews():
            self.print_output(self.users_reviews)
        if self.stats_issues():
            self.print_output(self.users_issues)
        if self.summarize():
            self._print_summarize_output()

    def name(self):
      return "stats"

    def stats(self):
        self.start_comment()
        if self.stats_commits():
            self._update_users_commits()
        if self.stats_prs():
            self._update_users_prs()
        if self.stats_reviews():
            self._update_users_reviews()
        if self.stats_issues():
            self._update_users_issues()
        self.print_stats_output()
        self.end_comment()
        return 0
