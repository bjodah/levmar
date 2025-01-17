#!/bin/bash
PKG_NAME=${1:-${CI_REPO##*/}}
env_path=$(compgen -G /opt-3/cpython-v3.*-apt-deb/bin)
if [ -e $env_path/activate ]; then
   source $env_path/activate
fi
PYTHON=python
$PYTHON setup.py sdist
( cd dist/; $PYTHON -m pip install $PKG_NAME-$($PYTHON ../setup.py --version).tar.gz )
./scripts/run_tests.sh --cov $PKG_NAME --cov-report html --pyargs $PKG_NAME

# Make sure repo is pip installable from git-archive zip
git archive -o /tmp/$PKG_NAME.zip HEAD
$PYTHON -m pip install --force-reinstall /tmp/$PKG_NAME.zip
( cd /; python3 -c "from ${PKG_NAME} import __version__; assert len(__version__.split('.')) >= 2" )
[ ! grep "DO-NOT-MERGE!" -R . --exclude ci.sh ]
