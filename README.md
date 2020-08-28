# ghtrack

Automate getting tracking commits, prs, reviews, and issues for group of GitHub users in repos from one organization.

# Getting started

There are two things you need to get started with the ghtrack CLI. From now on called CLI or `ght`.

First, you need to get a developer, or admin account, for your `GitHub` ID. [Register](https://developer.github.com/program/), it's free. When you do, you can then create an access token in order to use the GitHub APIs v3 (or later).

Second, you need to setup your [environment](#Environment). See that section for details. However, note also that you can either setup your local machine with Python3 and the dependencies, or, alternatively, use the included [`Dockerfile`](Dockerfile) to create a container with the latest version and all the dependencies setup for you. 

You can also use one of my published images, or best, the latest one here: `docker.io/drmax/ghtrack:latest`. And then run the image locally and start an interactive BASH session with:

```bash
docker run -it docker.io/drmax/ghtrack:latest /bin/bash
```

## Credentials

Once you have an access token for your Github account, make sure to copy and keep it safe.

You will need to use this access token while invoking the CLI. You can either pass the key with each invocation, via an environment variable, or adding it to a file.

1. Pass it locally using the `--access-token <GitHub access token here>`, without the '<>'

2. When using an environment variable, just set it as follows:

```bash
export GH_ACCESS_TOKEN=<GitHub access token here>
```

3. Alternatively, you can create a `.ghtrack.yml` file and add the key in there. Then `ght` will find the credentials for you automatically.

Create your `./.ghtrack.yml` file with a command as follows or with your favorite editor:

```bash
cat > .ghtrack.yml <<EOF
gh_access_token: <GitHub access token here>
EOF
```

*WARNING* needless to say that you should not share, nor checkin to GitHub, nor make public any access token or any credentials data.

## User guide

The following is a brief user guide for the `ght` CLI. You can see an abreviated version of this user guide by running `ght --help`

```bash
➜  ghtrack git:(master) ./ght -h
GitHub track

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

  --rate-limit                   Enables rate limiting (default or speficy --rt-* options).
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
```

### `commits`

The `commits` command group is used to get commit statistics.

#### Usage

```bash
ght commits march knative --users=maximilien \
                          --all-repos \
                          --output=CSV \
                          --show-all-stats \
                          --file=maximilien-march-knative.csv
```

#### Description

Collects all commits data for GitHub user 'maximilien' during the month of 'march' in all repos of the 'knative' organization and saves it into CSV file. All stats are displayed, so if 'maximilien' has 0 commits in a repo, the output will display 0.

### `prs`

The `prs` command group is used to get commit statistics.

#### Usage

```bash
ght prs apr knative --users=maximilien \
                    --all-repos \
                    --skip-repos=client,client-contrib \
                    --output=yaml \
                    --file=maximilien-april-all-but-client-client-repos.yml
```

#### Description

Collects all PRs data for GitHub user 'maximilien' during the month of 'april' (three letter abreviations are OK) in all repos of the 'knative' organization, except 'client' and 'client-contrib', and saves it into YAML file. Since `--show-all-stats` is not used, only repos for which user has `prs` will show in output.

### `reviews`

The `reviews` command group is used to get reviews statistics on 'open' or 'closed' (default) PRs.

#### Usage

```bash
ght reviews july  knative --users=maximilien,mattmore \
                          --repos=client \
                          --state=open \
                          --output=JSON
```

#### Description

Collects all reviews statistics, on 'open' PRs, for GitHub users 'maximilien' and 'mattmore' during the month of 'july' in the 'client' repo of the 'knative' organization and displays JSON in terminal.

#### Example Output

```bash
Getting reviews for 2 users in 1 repos via GitHub APIs... be patient
Getting 'reviews' for 'maximilien' in organization: 'knative'
[============================================================] 100.0% ...processing repos
Getting 'reviews' for 'mattmore' in organization: 'knative'
[=========================================================---] 94.7% ...processing repos

{
    "mattmore": {
        "client": 0
    },
    "maximilien": {
        "client": 2
    },
    "request": {
        "data": "reviews",
        "month": "july",
        "org": "knative",
        "state": "open",
        "year": 2020
    }
}
Showing only non-zero stats, use --show-all-stats to view all
OK
```

### `issues`

The `issues` command group is used to get issue statistics on 'open' or 'closed' (default) issues.

#### Usage

```bash
ght issues november knative --users=maximilien \
                            --repos=client,client-contrib \
                            --show-all-stats \
                            --output=txt
```

#### Description

Collects all issues statistics, counting only issues that are 'closed', for GitHub user 'maximilien' during the month of 'november' in 'client-contrib' repo of the 'knative' organization and shows it as text in standard output. Show all stats, even when 0.

#### Example Output

```bash
Getting issues for 1 users in 2 repos via GitHub APIs... be patient
Getting 'issues' for 'maximilien' in organization: 'knative'
[============================================================] 100.0% ...processing repos

org        year  month     data    state
-------  ------  --------  ------  -------
knative    2020  november  issues  closed

user        repo            data      count
----------  --------------  ------  -------
maximilien  client          issues        0
maximilien  client-contrib  issues        0
```

### `stats`

The `stats` command group is used to get statistics summary data for commits, prs, reviews, and issues.

#### Usage

```bash
ght stats june knative --users=maximilien \
                       --commits --prs --reviews --issues \
                       --all-repos \
                       --skip-repos=client,client-contrib
```

#### Description

Collects stats summary ('--commits', '--prs', '--reviews', and '--issues') data for GitHub user 'maximilien' during the month of 'june' in all repos except 'client' and 'client-contrib' repos of the 'knative' organization and display it in standard output.

You can of course specify a subset of flags: '--commits', '--prs', '--reviews', and '--issues', and only collect these statistics.

### common flags

Some additional documentation on common flags:

#### `--verbose`

Turn this on by simply using `--verbose` to see all output. The CLI by default shows a lot of output but with `--verbose` all output is shown.

#### `--summarize`

Using this flag for any of the commands will generate two additional table of data that summarize the data independent of users and per-repo. So the total number of commits, issues, reviews, and prs for each repo. This data is shown in two views [data, repo, total] and [repo, data, total]. For example:

```bash
./ght stats july knative --commits --issues --summarize \
                         --users=maximilien,octocat \
                         --repos=client,client-contrib \
                         --show-all-stats -o text 
Getting 'commits' for 'maximilien' in organization: 'knative'
[============================================================] 100.0% ...processing repos
...

org        year  month    data     state
-------  ------  -------  -------  -------
knative    2020  july     commits  closed

user        repo            data       count
----------  --------------  -------  -------
maximilien  client          commits        5
maximilien  client-contrib  commits        0
octocat     client          commits        0
octocat     client-contrib  commits        0

...

org        year  month    data    state
-------  ------  -------  ------  -------
knative    2020  july     issues  closed

user        repo            data      count
----------  --------------  ------  -------
maximilien  client          issues        0
maximilien  client-contrib  issues        0
octocat     client          issues        0
octocat     client-contrib  issues        0

repo            data       total
--------------  -------  -------
client          commits        5
client          prs            0
client          reviews        0
...

data     repo              total
-------  --------------  -------
commits  client                0
commits  client                5
commits  client-contrib        0
commits  client-contrib        5
...

OK
```

#### `--show-all-stats`

In many cases queries results end up with various entries with 0 total. For instance, user `octocat` has 0 reviews, prs, and commits. Using `--show-all-stats` will show an entry for all collected data (0 or not).

#### `--rate-limit`

Using the CLI for large queries (particularly for reviews) will end up with 100s of API calls to GitHub. While there places with `ght` could get faster by caching intermediate data and perhaps better total algorithms or using smarler data structure, none will solve the fundamental issue. 

The GitHub v3 public API is limited (publicly) in what we as end user can do. So various options are not allowed at this point. For instance, unlike commits query which is fast as it caches the data and returns totals for the past year, API calls for PR reviews and issues for instance are limited. You cannot do fine grained queries and even limit (in case of reviews) the dates for the query.

So in the current implementation, `ght` has to get all the data and process it locally. This is good for the GitHub server but bad for the local clients (`ght`). But as thw GitHub APIs is free, one cannot complain.

So one solution to avoid running into rate limiting errors (performing more API calls than allowed within a period of time), the CLI offers `--rate-limit` which allows the CLI to slow down its API invocations. This is done as follows:

1. Use `--rate-limit` and `ght` will automatically sleep periodically once it reaches some fixed number of API calls. 

2. Use `--rate-limit` and the associated `--rl-max` and `--rl-sleep` to specify the max number of API calls before sleeping. For instance the following call will rate limit after 5 API calls and sleep for 10 seconds before continueing:

```bash
/ght stats july knative --commits --issues --summarize \
                        --users=maximilien,octocat \
                        --repos=client,client-contrib \
                        --show-all-stats -o text \
                        --rate-limit --rl-max=5 --rl-sleep=10s

Getting 'commits' for 'maximilien' in organization: 'knative'
[============================================================] 100.0% ...processing repos
Getting 'commits' for 'octocat' in organization: 'knative'
[================================================------------] 80.0% ...processing repos
Warning: Rate limit API calls reach '5' and sleeping for '10' seconds
...
```

All of the various commands (stats, commits, prs, reviews, and issues) can use `--rate-limit` flags.

#### `--rate-limit-random`

Exactly like `--rate-limit` except that the value for max API calls and sleep is determine using a radom number generator selecting a random value between 1 and the value for max API calls or sleep.

## Workflows

TODO

# Developing

We welcome your contributions. You can do so by opening [issues](/issues) for features and bugs you find. Or you can submit [PRs](/pulls) when you have specific changes you would like to suggest. These changes can be both for source code, tests, and docs.

## Environment

This CLI uses Python 3.0 or later. Please [download Python 3](https://www.python.org/downloads/) for your particular environment to get started.

### Local

To run this CLI in your local machine. Besides Python 3 you will also need to install some dependencies. You can do so using Python's `pip` tool. Fist ensure [`pip` is installed](https://pip.pypa.io/en/stable/installing/) on your machine.

Once `pip` is installed, then install the dependencies with:

```bash
pip install PyGitHub==1.51
pip install PyYAML==5.3.1
pip install docopt==0.6.2
pip install tabulate==0.8.7
```

You can verify that your system is running by running the unit tests: `./hack/build.sh --test`.

Also run the CLI help with: `ght --help`

### Container

Alternatively, you can use `docker.io/drmax/ghtrack:latest` public image. Instantiate it. Get access to it via a command line shell and use the tool there. This image has all dependencies and code for `ght`. The following command should do this:

```bash
docker run -it docker.io/drmax/ghtrack:latest /bin/bash
```

### Create image

If you set your the environment variable 'DOCKER_USERNAME' with your [Docker Hub](https://hub.docker.com/) username and you install the [docker tooling](https://docs.docker.com/get-docker/), then you can generate a Docker container image by running `./hack/build.sh --docker`. The image will contain all dependencies and this tool source code.

## Testing

The code includes both unit tests and integration tests. You can run all unit tests by invoking: `./hack/build.sh --tests`.

Integration tests will require you to have a GitHub access token in a file called `.ghtrack.yml` or setting the access token in an environment variable called `GH_ACCESS_TOKEN`. You can then invoke `./build/build.sh --e2e` to run the integration tests.

You can run both types of tests in sequence with `./hack/build.sh --tests`

Once you can run all the tests. Please make your changes, add more tests, verify that all tests are still passing. Create and submit a PR.

# Next steps?

The following are immediate next steps:

1. add some common workflows (e.g., get reviews in last two months for k8s or knative)
2. look how to speed up some of the operations by caching intermediary data or Github APIs calls
3. make e2e tests faster (which might get there with solution for 2)