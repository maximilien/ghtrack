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

from github import Github

from common import *

class GHClient:
    def __init__(self, access_token, client=None):
        self.client = client
        self.access_token = access_token

    def __week_in(self, week_date, start_date, end_date):
        week_number = week_date.date().isocalendar()[1]
        start_week = start_date.date().isocalendar()[1]
        end_week = end_date.date().isocalendar()[1]
        if week_number >= start_week and week_number <= end_week:
            return True
        return False

    def get_client(self):
        if self.client == None:
            self.client = Github(self.access_token)
        return self.client

    def repos(self, org):
        ghorg = self.get_client().get_organization(org)
        return ghorg.get_repos()

    def reviews_count(self, repo, author_login, start_date, end_date, pr_state='close'):
        prs = repo.get_pulls(state=pr_state)
        reviews_count = 0
        for pr in prs:
            reviews = pr.get_reviews()
            for r in reviews:
                try:
                    if r.user.login == author_login and (r.submitted_at >= start_date and r.submitted_at <= end_date):
                        reviews_count += 1
                except Exception as e:
                    Console.warn("problem reading review: {r_id} from pr: {pr_id}, message: {message}".format(r_id=r.id, pr_id=pr.id, message=e.__str__()))
        return reviews_count

    def prs_count(self, repo, author_login, start_date, end_date, state='close'):
        prs = repo.get_pulls(state=state)
        prs_count = 0
        for pr in prs:
            if pr.user.login == author_login and (pr.created_at >= start_date and pr.created_at <= end_date):
                prs_count += 1
        return prs_count

    def issues_count(self, repo, author_login, start_date, end_date, state='close'):
        issues = repo.get_issues(state=state, since=start_date)
        issues_count = 0
        for i in issues:
            if i.user.login == author_login and (i.created_at >= start_date and i.created_at <= end_date):
                issues_count += 1
        return issues_count

    def commits_count(self, repo, author_login, start_date, end_date):
        commits_count = 0
        for sc in repo.get_stats_contributors():
            if sc.author.login == author_login:
                for w in sc.weeks:
                    if self.__week_in(w.w, start_date, end_date): 
                        commits_count += w.c
        return commits_count
