#!/usr/bin/env python3
import os

from os.path import join, dirname, realpath
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize
import numpy as np
import os
import sys

with open(join("mujoco_py", "version.py")) as version_file:
    exec(version_file.read())


def read_requirements_file(filename):
    req_file_path = '%s/%s' % (dirname(realpath(__file__)), filename)
    with open(req_file_path) as f:
        return [line.strip() for line in f]


packages = find_packages()
# Ensure that we don't pollute the global namespace.
for p in packages:
    assert p == 'mujoco_py' or p.startswith('mujoco_py.')


MISSING_MUJOCO_MESSAGE = '''
You appear to be missing MuJoCo.  We expected to find the file here: {}

This package only provides python bindings, the library must be installed separately.

Please follow the instructions on the README to install MuJoCo

    https://github.com/openai/mujoco-py#install-mujoco

Which can be downloaded from the website

    https://www.roboti.us/index.html
'''

def discover_mujoco():
    """
    Discovers where MuJoCo is located in the file system.
    Currently assumes path is in ~/.mujoco

    Returns:
    - mujoco_path (str): Path to MuJoCo 2.1 directory.
    """
    mujoco_path = os.getenv('MUJOCO_PY_MUJOCO_PATH')
    if not mujoco_path:
        mujoco_path = join(os.path.expanduser('~'), '.mujoco', 'mujoco210')

    # We get lots of github issues that seem to be missing these
    # so check that mujoco is really there and raise errors if not.
    if not os.path.exists(mujoco_path):
        message = MISSING_MUJOCO_MESSAGE.format(mujoco_path)
        print(message, file=sys.stderr)
        raise Exception(message)

    return mujoco_path

mujoco_path = discover_mujoco()

extension = Extension(
    'mujoco_py.cymj',
    sources=["mujoco_py/cymj.pyx", "mujoco_py/gl/osmesashim.c"],
    include_dirs=[
        "mujoco_py",
        os.path.join(mujoco_path, 'include'),
        np.get_include(),
    ],
    libraries=['mujoco210'] + ['glewosmesa', 'OSMesa', 'GL'],
    library_dirs=[join(mujoco_path, 'bin')],
    extra_compile_args=[
        '-fopenmp',  # needed for OpenMP
        '-w',  # suppress numpy compilation warnings
    ],
    extra_link_args=['-fopenmp'],
    runtime_library_dirs=[join(mujoco_path, 'bin')],
    language='c')


setup(
    name='mujoco-py',
    version=__version__,  # noqa
    author='OpenAI Robotics Team',
    author_email='robotics@openai.com',
    url='https://github.com/openai/mujoco-py',
    packages=packages,
    include_package_data=True,
    ext_modules=cythonize([extension]),
    package_dir={'mujoco_py': 'mujoco_py'},
    package_data={'mujoco_py': ['generated/*.so']},
    install_requires=read_requirements_file('requirements.txt'),
    tests_require=read_requirements_file('requirements.dev.txt'),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
