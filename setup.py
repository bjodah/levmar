#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import pprint
import shutil
import platform
import warnings
from glob import glob
from setuptools import Extension, setup
from setuptools import dist
from Cython.Build import cythonize
import numpy as np


dist.Distribution().fetch_build_eggs(['Cython>=0.15.1', 'numpy>=1.10'])
pkg_name = 'levmar'
url = 'https://github.com/bjodah/' + pkg_name
license = 'GNU General Public Licence v2'  # Takeshi Kanmae's wrapper code has the MIT license

levmar_sources = [
    'levmar/levmar-2.6/lm.c',
    'levmar/levmar-2.6/Axb.c',
    'levmar/levmar-2.6/misc.c',
    'levmar/levmar-2.6/lmlec.c',
    'levmar/levmar-2.6/lmbc.c',
    'levmar/levmar-2.6/lmblec.c',
    'levmar/levmar-2.6/lmbleic.c'
]


def _path_under_setup(*args):
    return os.path.join(*args)


release_py_path = _path_under_setup(pkg_name, '_release.py')
config_py_path = _path_under_setup(pkg_name, '_config.py')
env = None  # silence pyflakes, 'env' is actually set on the next line
exec(open(config_py_path).read())
for k, v in list(env.items()):
    env[k] = os.environ.get('%s_%s' % (pkg_name.upper(), k), v)

is_win = True if 'win' in platform.platform().lower() else False

if is_win:
    libs = ['cbia.lib.blas.dyn.rel.x64.12', 'cbia.lib.lapack.dyn.rel.x64.12'] if is_win else []
else:
    libs = [env[l] for l in ['LAPACK', 'BLAS'] if env[l]]

extensions = Extension('%s._levmar' % pkg_name,
                       [os.path.join('levmar', '_levmar.pyx')] + levmar_sources,
                       libraries=libs,
                       library_dirs=['libs/'],
                       )

ext_modules = cythonize(extensions)

_version_env_var = '%s_RELEASE_VERSION' % pkg_name.upper()
RELEASE_VERSION = os.environ.get(_version_env_var, '')

# http://conda.pydata.org/docs/build.html#environment-variables-set-during-the-build-process
if os.environ.get('CONDA_BUILD', '0') == '1':
    try:
        RELEASE_VERSION = 'v' + open(
            '__conda_version__.txt', 'rt').readline().rstrip()
    except IOError:
        pass


if len(RELEASE_VERSION) > 1:
    if RELEASE_VERSION[0] != 'v':
        raise ValueError("$%s does not start with 'v'" % _version_env_var)
    TAGGED_RELEASE = True
    __version__ = RELEASE_VERSION[1:]
else:  # set `__version__` from _release.py:
    TAGGED_RELEASE = False
    exec(open(release_py_path).read())

classifiers = [
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Mathematics',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
]

tests = [
    '%s.tests' % pkg_name,
]

with io.open(_path_under_setup(pkg_name, '__init__.py'), 'rt', encoding='utf-8') as f:
    short_description = f.read().split('"""')[1].split('\n')[1]
if not 10 < len(short_description) < 255:
    warnings.warn("Short description from __init__.py proably not read correctly")
long_descr = io.open(_path_under_setup('README.rst'), encoding='utf-8').read()
if not len(long_descr) > 100:
    warnings.warn("Long description from README.rst probably not read correctly.")
_author, _author_email = io.open(_path_under_setup('AUTHORS'), 'rt', encoding='utf-8').readline().split('<')
_author_email = _author_email.split('>')[0].strip() if '@' in _author_email else None

setup_kwargs = dict(
    name=pkg_name,
    version=__version__,
    description=short_description,
    long_description=long_descr,
    classifiers=classifiers,
    author=_author.strip(),
    author_email=_author_email,
    maintainer='Björn Dahlgren',
    maintainer_email='bjodah@gmail.com',
    url=url,
    license=license,
    packages=[pkg_name] + tests,
    include_dirs=['levmar/levmar-2.6', np.get_include()],
    ext_modules=ext_modules,
    data_files=[('lib/site-packages/' + pkg_name, glob('libs/*.dll'))],
    # cmdclass = {'build_ext': build_ext},
    install_requires=['numpy', 'nose', 'icc_rt'],
    extras_require={'docs': ['Sphinx', 'sphinx_rtd_theme', 'numpydoc']},
)

if __name__ == '__main__':
    try:
        if TAGGED_RELEASE:
            # Same commit should generate different sdist
            # depending on tagged version (set PYGSLODEIV2_RELEASE_VERSION)
            # this will ensure source distributions contain the correct version
            shutil.move(release_py_path, release_py_path+'__temp__')
            open(release_py_path, 'wt').write(
                "__version__ = '{}'\n".format(__version__))
        shutil.move(config_py_path, config_py_path+'__temp__')
        open(config_py_path, 'wt').write("env = {}\n".format(pprint.pformat(env)))
        setup(**setup_kwargs)
    finally:
        if TAGGED_RELEASE:
            shutil.move(release_py_path+'__temp__', release_py_path)
        shutil.move(config_py_path+'__temp__', config_py_path)
