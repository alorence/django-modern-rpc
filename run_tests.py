#! /usr/bin/env python
from __future__ import print_function

import subprocess

import pytest


if __name__ == '__main__':

    return_codes = []

    print('Running py.test')
    ret = pytest.main()
    print('py.test failed' if ret else 'py.test passed')
    return_codes.append(ret)

    print('Running flake8')
    ret = subprocess.call(['flake8'])
    print('flake8 failed' if ret else 'flake8 passed')
    return_codes.append(ret)

    print('')

    exit(0 if all([x == 0 for x in return_codes]) else 1)
