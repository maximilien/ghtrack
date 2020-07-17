# ghtrack

Automate getting tracking commits, reviews, and issues for group of GitHub users.

# Getting started

There are two things you need to get started with the ghtrack CLI. From now on called CLI or `ght`.

First, you need to get a developer or admin account on your `GitHub` ID. When you do, can create an access token to use the GitHub APIs v3 or later.

Second, you need to setup your [environment](#Environment). See that section for details. However, note that you can either setup your local machine with Python3 and dependencies or better use the `Dockerfile` to create a container with all the details. You can also use one of my publish images: `dockerhub.io/drmax/ghtrack:latest`.

## Credentials

Once you have created access token for your Github account. Make sure to copy and keep it safe.

You will need to use it while invoking the CLI. You can either pass the key with each invokation.

Or as a shortcut, you can create a `.ghtrack.yml` file and add the key in there. Then `ght` will find the credentials for you automatically.

Create your `./.ghtrack.yml` file with a command as follows or with your favorite editor:

```bash
cat > .ghtrack.yml <<EOF
# GitHub
access_token: [GitHub access token here]
EOF
```

*WARNING* needless to say that you should not share not checkin to GitHub nor make public any access token or credentials data.

## User guide

The following is a brief user guide for the `ght` CLI. You can see an abreviated version of this user guide by running `ght --help`

```bash
➜  ghtrack git:(master) ✗ ght -h
GitHub track

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
  --org=organization.            The GitHub organization.

  --all-repos                    Track all repositories in GitHub organization.
  --repos=repo1,repo2,...        List of repositories in GitHub organization to track.
  --skip-repos=repo1,repo2,...   List of repositories in GitHub organization to skip.

  -a --access-token=ACCESS_TOKEN Your GitHub access token to access GitHub APIs.
  -o --output-file=FILE          The file path to save results CSV file.

  -h --help                      Show this screen.
  -v --version                   Show version.
```

### `commits`

The `commits` command group is used to get commit stats.

Usage:

```bash
ght commits march --users=maximilien \
                  --org=knative --all-repos \
                  --output-file=maximilien-march-knative.csv
```

Description:

Collects all commits data for GitHub user 'maximilien' during the month of 'march' in all repos of the 'knative' organization and saves it into CSV file.

### `reviews`

The `reviews` command group is used to get reviews data on open and closed PRs.

Usage:

```bash
ght reviews july --users=maximilien,mattmore \
                 --org=knative --repos=client \
                 --output-file=maximilien-mattmore-july-client.csv
```

Description:

Collects all reviews data for GitHub users 'maximilien' and 'mattmore' during the month of 'july' in all 'client' repo of the 'knative' organization and saves it into CSV file.

### `issues`

The `issues` command group is used to get issue data on open and closed issues.

Usage:

```bash
ght issues november --users=maximilien \
                    --org=knative --repos=client-contrib \
                    --output-file=maximilien-mattmote-november-client-contrib.csv
```

Description:

Collects all issues data for GitHub user 'maximilien' during the month of 'november' in 'client-contrib' repo of the 'knative' organization and saves it into CSV file.

### `stats`

The `stats` command group is used to get stats summary data for commits, reviews, and issues.

Usage:

```bash
ght stats june --users=maximilien \
               --org=knative --repos=client,client-contrib \
               --output-file=maximilien-june-client-client-contrib.csv
```

Description:

Collects all stats summary data for GitHub user 'maximilien' during the month of 'june' in 'client' and 'client-contrib' repos of the 'knative' organization and saves it into CSV file.

## Workflows

TODO

# Developing

We welcome your contributions. You can do so by opening [issues](/issues) for features and bugs you find. Or you can submit [PRs](/pulls) when you have specific changes you would like to make. These changes can be both for source code, tests, and docs.

## Environment

This CLI uses Python 3.0 or later. Please [download Python 3](https://www.python.org/downloads/) for your particular environment to get started.

### Local

To run this CLI in your local machine. Besides Python 3 you will also need to install some dependencies. You can do so using Python's `pip` tool. Fist ensure [`pip` is installed](https://pip.pypa.io/en/stable/installing/) on your machine.

Once `pip` is installed, then install the dependencies with:

```bash
pip install pygithub
```

You can verify that your system is running by running the unit tests: `./hack/build.sh --test`.

Also run the CLI help with: `ght --help`

### Container

You can use `docker.io/maximilien/ghtrack:latest` public image. Instantiate it. Get access to it via a command line shell and use the tool. This image has all dependencies.

### Create Image

If you set your the environment variable with your 'DOCKER_USERNAME' and you install the docker tooling, then you can generate a docker image that you can use to run this tool using `./hack/build.sh --docker`. The image will contain all dependencies and this tool.

## Testing

The code includes both unit tests and integration tests. You can run all unit tests by invoking: `./hack/build.sh --test`.

Integration tests will require you to have a GitHub access token in a file called `.ghtrack.yml`. You can then invoke `./build/build.sh --e2e` to run the integration tests.

You can run both types of tests with `./hack/build.sh --all`

Once you can run all the tests. Please make your changes, add more tests, verify that all tests are passing. Create and submit a PR.

# Next steps?

The following are immediate next steps:
