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

import time
from datetime import datetime

from github import Github

from common import *

class GHClient:
    def __init__(self, access_token, client=None):
        self.client = client
        self.access_token = access_token
        self.rate_limit_data = RateLimitData(0, 0)
        self.api_calls = 0

    def _week_in(self, week_date, start_date, end_date):
        week_number = week_date.date().isocalendar()[1]
        start_week = start_date.date().isocalendar()[1]
        end_week = end_date.date().isocalendar()[1]
        if week_number >= start_week and week_number <= end_week:
            return True
        return False

    def _init_authors_count_map(self, authors):
        authors_count = {}
        for author in authors:
            authors_count[author] = 0
        return authors_count

    def _count_check_api_calls(self):
        if not self.rate_limit_data.enabled:
            return
        self.api_calls += 1
        if self.api_calls >= self.rate_limit_data.max_calls():
            Console.println()
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            Console.warn("{current_time} Rate limit API calls reach '{max_calls}' and sleeping for '{sleep}' seconds".format(current_time=current_time, max_calls=self.rate_limit_data.max_calls(), sleep=self.rate_limit_data.sleep()))
            time.sleep(self.rate_limit_data.sleep())
            self.api_calls = 0

    def set_rate_limit_data(self, rl):
        self.rate_limit_data = rl

    def get_client(self):
        if self.client == None:
            self.client = Github(self.access_token)
        return self.client

    def repos(self, org):
        self._count_check_api_calls()
        ghorg = self.get_client().get_organization(org)
        return ghorg.get_repos()

    def reviews_count(self, repo, author, start_date, end_date, pr_state='close'):
        self._count_check_api_calls()
        prs = repo.get_pulls(state=pr_state)
        reviews_count = 0
        for pr in prs:
            self._count_check_api_calls()
            reviews = pr.get_reviews()
            for r in reviews:
                try:
                    if r.user.login == author and (r.submitted_at >= start_date and r.submitted_at <= end_date):
                        reviews_count += 1
                except Exception as e:
                    Console.warn("problem reading review: {r_id} from pr: {pr_id}, message: {message}".format(r_id=r.id, pr_id=pr.id, message=e.__str__()))
        return reviews_count

    def reviews_counts(self, repo, authors, start_date, end_date, pr_state='close'):
        self._count_check_api_calls()
        prs = repo.get_pulls(state=pr_state)
        reviews_counts = self._init_authors_count_map(authors)
        for pr in prs:
            self._count_check_api_calls()
            reviews = pr.get_reviews()
            for r in reviews:
                try:
                    if r.user.login in authors and (r.submitted_at >= start_date and r.submitted_at <= end_date):
                        if r.user.login in reviews_counts:
                            reviews_counts[r.user.login] += 1
                except Exception as e:
                    Console.warn("problem reading review: {r_id} from pr: {pr_id}, message: {message}".format(r_id=r.id, pr_id=pr.id, message=e.__str__()))
        return reviews_counts

    def prs_count(self, repo, author, start_date, end_date, state='close'):
        self._count_check_api_calls()
        prs = repo.get_pulls(state=state)
        prs_count = 0
        for pr in prs:
            if pr.user.login == author and (pr.created_at >= start_date and pr.created_at <= end_date):
                prs_count += 1
        return prs_count

    def prs_counts(self, repo, authors, start_date, end_date, state='close'):
        self._count_check_api_calls()
        prs = repo.get_pulls(state=state)
        prs_counts = self._init_authors_count_map(authors)
        for pr in prs:
            if pr.user.login in authors and (pr.created_at >= start_date and pr.created_at <= end_date):
                if pr.user.login in prs_counts:
                    prs_counts[pr.user.login] += 1
        return prs_counts

    def issues_count(self, repo, author, start_date, end_date, state='close'):
        self._count_check_api_calls()
        issues = repo.get_issues(state=state, since=start_date)
        issues_count = 0
        for i in issues:
            if i.user.login == author and (i.created_at >= start_date and i.created_at <= end_date):
                issues_count += 1
        return issues_count

    def issues_counts(self, repo, authors, start_date, end_date, state='close'):
        self._count_check_api_calls()
        issues = repo.get_issues(state=state, since=start_date)
        issues_counts = self._init_authors_count_map(authors)
        for i in issues:
            if i.user.login in authors and (i.created_at >= start_date and i.created_at <= end_date):
                if i.user.login in issues_counts:
                    issues_counts[i.user.login] += 1
        return issues_counts

    def commits_count(self, repo, author, start_date, end_date):
        commits_count = 0
        self._count_check_api_calls()
        try:
            for sc in repo.get_stats_contributors():
                if sc.author.login == author:
                    for w in sc.weeks:
                        if self._week_in(w.w, start_date, end_date):
                            commits_count += w.c
        except TypeError as e:
            print(f"{e} is a NoneType")
        return commits_count

    def commits_counts(self, repo, authors, start_date, end_date):
        commits_counts = self._init_authors_count_map(authors)
        self._count_check_api_calls()
        for sc in repo.get_stats_contributors():
            if sc.author.login in authors:
                for w in sc.weeks:
                    if self._week_in(w.w, start_date, end_date):
                        if sc.author.login in commits_counts:
                            commits_counts[sc.author.login] += w.c
        return commits_counts
