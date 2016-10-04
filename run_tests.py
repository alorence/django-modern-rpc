#! /usr/bin/env python
from __future__ import print_function

import subprocess

import pytest


if __name__ == '__main__':

    print('Running py.test')
    ret = pytest.main()
    print('py.test failed' if ret else 'py.test passed')

    print('Running flake8')
    ret = subprocess.call(['flake8'])
    print('flake8 failed' if ret else 'flake8 passed')
    print('')
