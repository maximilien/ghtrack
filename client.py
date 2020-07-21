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

class GHClient:
    def __init__(self, access_token):
        self.client = None
        self.access_token = access_token

    def get_client(self):
        if self.client == None:
            self.client = Github(self.access_token)
        return self.client

    def repos(self, org):
        ghorg = self.get_client().get_organization(org)
        return ghorg.get_repos()

    def issue_count(self, repo, author_login, start_date, end_date, state='open'):
        issues = repo.get_issues(state=state)
        issue_count = 0
        for i in issues:
            if i.user.login == author_login and (i.created_at >= start_date and i.created_at <= end_date):
                issue_count += 1
        return issue_count

    def commits(self):
        return None

    def reviews(self):
        return None
