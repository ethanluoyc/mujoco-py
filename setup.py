#!/usr/bin/env python3
import os

from os.path import join, dirname, realpath
from setuptools import Extension, setup, find_packages
from Cython.Build import cythonize
import numpy as np
import importlib

def read_requirements_file(filename):
    req_file_path = '%s/%s' % (dirname(realpath(__file__)), filename)
    with open(req_file_path) as f:
        return [line.strip() for line in f]


packages = find_packages()
# Ensure that we don't pollute the global namespace.
for p in packages:
    assert p == 'mujoco_py' or p.startswith('mujoco_py.')

def load_utils_module(pkg_path):
    spec = importlib.util.spec_from_file_location(
        'utils', os.path.join(pkg_path, 'utils.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def load_version_module(pkg_path):
    spec = importlib.util.spec_from_file_location(
        'version', os.path.join(pkg_path, 'version.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

utils_module = load_utils_module("mujoco_py")
version_module = load_version_module("mujoco_py")
mujoco_path = utils_module.discover_mujoco()

# TODO(yl): 
# 1. Reuse from the mujoco_py/builder.py
# 2. Support EGL rendering
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
        # '-fopenmp',  # needed for OpenMP
        '-w',  # suppress numpy compilation warnings
    ],
    # extra_link_args=['-fopenmp'],
    # runtime_library_dirs=[join(mujoco_path, 'bin')],
    language='c')


setup(
    name='mujoco-py',
    version=version_module.__version__,  # noqa
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
