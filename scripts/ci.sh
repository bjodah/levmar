#!/bin/bash -xe
PKG_NAME=${1:-${CI_REPO##*/}}
if [[ "$CI_BRANCH" =~ ^v[0-9]+.[0-9]?* ]]; then
    eval export ${PKG_NAME^^}_RELEASE_VERSION=\$CI_BRANCH
    echo ${CI_BRANCH} | tail -c +2 > __conda_version__.txt
fi
PYTHON=${PYTHON:-python3}

$PYTHON setup.py sdist
PKG_VERSION=$($PYTHON setup.py --version)
(cd dist/; $PYTHON -m pip install $PKG_NAME-$PKG_VERSION.tar.gz)
(cd /; $PYTHON -m pytest --pyargs $PKG_NAME)
$PYTHON -m pip install --user -e .[all]
PYTHONPATH=$(pwd) ./scripts/run_tests.sh --cov $PKG_NAME --cov-report html
./scripts/coverage_badge.py htmlcov/ htmlcov/coverage.svg

# Make sure repo is pip installable from git-archive zip
git archive -o /tmp/$PKG_NAME.zip HEAD
$PYTHON -m pip install --force-reinstall /tmp/$PKG_NAME.zip
(cd /; python3 -c "from ${PKG_NAME} import __version__; assert len(__version__.split('.')) >= 2")

! grep "DO-NOT-MERGE!" -R . --exclude ci.sh
