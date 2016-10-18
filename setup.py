#!/usr/bin/env python
import re
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


def read(*names, **kwargs):
    with open(
        path.join(path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='django-modern-rpc',
    version=find_version("modernrpc", "__init__.py"),
    description='Simple and modern JSON-RPC and XML-RPC server implementation for Django',
    long_description=read('README.rst'),
    author='Antoine Lorence',
    author_email='antoine.lorence@gmail.com',
    url='https://github.com/alorence/django-modern-rpc',
    packages=find_packages(exclude=['modernrpc.tests', 'modernrpc.tests.*']),
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
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
