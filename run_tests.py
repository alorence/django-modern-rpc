#! /usr/bin/env python
from __future__ import print_function

import subprocess


def fail_on_error(return_code):
    if return_code:
        print('Failed !')
        exit(return_code)
    else:
        print('Success !')


if __name__ == '__main__':

    print('Running py.test & coverage analyze')
    subprocess.call(['coverage run --source modernrpc pytest .'])

    print('Running flake8')
    fail_on_error(subprocess.call(['flake8']))

    exit(0)
