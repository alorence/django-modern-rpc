#!/usr/bin/env python
from setuptools import setup, find_packages

import modernrpc


setup(
    name='django-modern-rpc',
    version=modernrpc.__version__,
    description='Simple and modern RPC Server for Django',
    long_description=open('README.rst').read(),
    author='Antoine Lorence',
    author_email='antoine.lorence@gmail.com',
    url='https://github.com/alorence/django-modern-rpc',
    packages=find_packages(exclude=('testsite', 'modernrpc.tests',)),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django :: 1.10",
        "Framework :: Django :: 1.9",
        "Framework :: Django :: 1.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Intended Audience :: Developers",
    ],
    install_requires=[
        "Django>=1.8.0",
    ]
)
