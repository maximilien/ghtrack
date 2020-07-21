#!/bin/bash

# Copyright 2020 IBM
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

set -o pipefail

docker_username=${DOCKER_USERNAME:-}
source_dirs="."

# Store for later
if [ -z "$1" ]; then
    ARGS=("")
else
    ARGS=("$@")
fi

set -eu

# Run build
run() {
  # Jump into project directory
  pushd $(basedir) >/dev/null 2>&1

  # Print help if requested
  if $(has_flag --help -h); then
    display_help
    exit 0
  fi

  # Fast mode: Only compile and maybe run test
  if $(has_flag --fast -f); then
    py_build

    if $(has_flag --test -t); then
       py_test
    fi
    exit 0
  fi

  # Run only UT tests
  if $(has_flag --test -t); then
    py_test
    exit 0
  fi

  # Run only e2e tests
  if $(has_flag --e2e -e); then
    py_e2e
    exit 0
  fi

  # Run only all tests
  if $(has_flag --tests -T); then
    py_test
    py_e2e
    exit 0
  fi

  # Run docker-image and docker-push
  if $(has_flag --docker -d); then
    if [[ -z "${docker_username}" ]]; then
      echo "Please set environment variable DOCKER_USERNAME"
      exit 1
    fi
    docker_build_image
    docker_push_image
    exit 0
  fi

  # Run only docker-image
  if $(has_flag --docker-image); then
    if [[ -z "${docker_username}" ]]; then
      echo "Please set environment variable DOCKER_USERNAME"
      exit 1
    fi
    docker_build_image
    exit 0
  fi

  # Run only docker-push
  if $(has_flag --docker-push); then
    if [[ -z "${docker_username}" ]]; then
      echo "Please set environment variable DOCKER_USERNAME"
      exit 1
    fi
    docker_push_image
    exit 0
  fi

  # Run only e2e tests
  if $(has_flag --all -a); then
    py_build
    py_test
    py_e2e
    echo "────────────────────────────────────────────"
    ./ght --version
    exit 0
  fi

  # Default flow
  py_build
  py_test

  echo "────────────────────────────────────────────"
  ./ght --version
}

docker_build_image() {
  echo "🚧 🐳 build image"
  docker build -f ./Dockerfile -t ${DOCKER_USERNAME}/ghtrack .
}

docker_push_image() {
  echo "🐳 push image"
  docker push ${DOCKER_USERNAME}/ghtrack
}

py_build() {
  echo "🚧 Nothing to build (python3)"
  echo "🧹 Linting *.py sources"
}

py_test() {
  local test_output=$(mktemp /tmp/ghtrack-test-output.XXXXXX)

  local red=""
  local reset=""
  # Use color only when a terminal is set
  if [ -t 1 ]; then
    red="[31m"
    reset="[39m"
  fi

  echo "🧪 ${X}Tests"
  set +e
  python3 -m unittest *_test.py >$test_output 2>&1
  local err=$?
  if [ $err -ne 0 ]; then
    echo "🔥 ${red}Failure${reset}"
    cat $test_output | sed -e "s/^.*\(FAIL.*\)$/$red\1$reset/"
    rm $test_output
    exit $err
  fi
  rm $test_output
}

py_e2e() {
  local e2e_output=$(mktemp /tmp/ghtrack-e2e-output.XXXXXX)

  local red=""
  local reset=""
  # Use color only when a terminal is set
  if [ -t 1 ]; then
    red="[31m"
    reset="[39m"
  fi

  echo "🧪 e2e ${X}Tests"
  set +e
  check_credentials
  cd test
  ./local-e2e-tests.sh >$e2e_output 2>&1
  local err=$?
  if [ $err -ne 0 ]; then
    echo "🔥 ${red}Failure${reset}"
    cat $e2e_output | sed -e "s/^.*\(FAIL.*\)$/$red\1$reset/"
    rm $e2e_output
    exit $err
  fi
  cd ..
  rm $e2e_output
}

check_credentials() {
  if [ ! -f ./.ghtrack.yml ]; then
    echo "🔥 Could not find .ghtrack.yml.yml file"
    exit -1
  fi
}

check_license() {
  echo "⚖️ ${S}License"
  local required_keywords=("Authors" "Apache License" "LICENSE-2.0")
  local extensions_to_check=("sh" "py" "yaml" "yml" "json")

  local check_output=$(mktemp /tmp/ghtrack-licence-check.XXXXXX)
  for ext in "${extensions_to_check[@]}"; do
    find . -name "*.$ext" -a \! -path "./vendor/*" -a \! -path "./.*" -print0 |
      while IFS= read -r -d '' path; do
        for rword in "${required_keywords[@]}"; do
          if ! grep -q "$rword" "$path"; then
            echo "   $path" >> $check_output
          fi
        done
      done
  done
  if [ -s $check_output ]; then
    echo "🔥 No license header found in:"
    cat $check_output | sort | uniq
    echo "🔥 Please fix and retry."
    rm $check_output
    exit 1
  fi
  rm $check_output
}


update_deps() {
  echo "🚒 Update"
}

# Dir where this script is located
basedir() {
    # Default is current directory
    local script=${BASH_SOURCE[0]}

    # Resolve symbolic links
    if [ -L $script ]; then
        if readlink -f $script >/dev/null 2>&1; then
            script=$(readlink -f $script)
        elif readlink $script >/dev/null 2>&1; then
            script=$(readlink $script)
        elif realpath $script >/dev/null 2>&1; then
            script=$(realpath $script)
        else
            echo "ERROR: Cannot resolve symbolic link $script"
            exit 1
        fi
    fi

    local dir=$(dirname "$script")
    local full_dir=$(cd "${dir}/.." && pwd)
    echo ${full_dir}
}

# Checks if a flag is present in the arguments.
has_flag() {
    filters="$@"
    for var in "${ARGS[@]}"; do
        for filter in $filters; do
          if [ "$var" = "$filter" ]; then
              echo 'true'
              return
          fi
        done
    done
    echo 'false'
}

# Spaced fillers needed for certain emojis in certain terminals
S=""
X=""

# Calculate space fixing variables S and X
apply_emoji_fixes() {
  # Temporary fix for iTerm issue https://gitlab.com/gnachman/iterm2/issues/7901
  if [ -n "${ITERM_PROFILE:-}" ]; then
    S=" "
    # This issue has been fixed with iTerm2 3.3.7, so let's check for this
    # We can remove this code alltogether if iTerm2 3.3.7 is in common usage everywhere
    if [ -n "${TERM_PROGRAM_VERSION}" ]; then
      args=$(echo $TERM_PROGRAM_VERSION | sed -e 's#[^0-9]*\([0-9]*\)[.]\([0-9]*\)[.]\([0-9]*\)\([0-9A-Za-z-]*\)#\1 \2 \3#')
      expanded=$(printf '%03d%03d%03d' $args)
      if [ $expanded -lt "003003007" ]; then
        X=" "
      fi
    fi
  fi
}

# Display a help message.
display_help() {
    local command="${1:-}"
    cat <<EOT
GH Track build script

Usage: $(basename $BASH_SOURCE) [... options ...]

with the following options:

-a  --all                     Run all build, unit and e2e tests
-f  --fast                    Only compile (without dep update, formatting, testing, doc gen)
-t  --test                    Run the UT tests when used with --fast or --watch
-e  --e2e                     Run the e2e tests when used with --fast or --watch
-T  --tests                   Run the UT and e2e tests
-d  --docker                  Generates Docker image and push using DOCKER_USERNAME
    --docker-image            Generates Docker image only
    --docker-push             Pushes Docker image using DOCKER_USERNAME
-h  --help                    Display this help message
    --verbose                 More output
    --debug                   Debug information for this script (set -x)

You can add a symbolic link to this build script into your PATH so that it can be
called from everywhere. E.g.:

ln -s $(basedir)/hack/build.sh /usr/local/bin/ghtrack.sh

Examples:

* Run build and test: ................ build.sh
* Run only UT tests:.................. build.sh --test
* Run only e2e tests: ................ build.sh --e2e
* Run all tests: ..................... build.sh --tests
* Compile with tests: ................ build.sh -f -t
* Generate and push docker image: .... build.sh --docker
* Build and all and tests: ........... build.sh --all
EOT
}

if $(has_flag --debug); then
    export PS4='+($(basename ${BASH_SOURCE[0]}):${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
    set -x
fi

# Shared funcs with CI
source $(basedir)/hack/build-flags.sh

# Fixe emoji labels for certain terminals
apply_emoji_fixes

run $*
