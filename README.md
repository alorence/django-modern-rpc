# django-modern-rpc

[![Downloads](https://static.pepy.tech/personalized-badge/django-modern-rpc?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads)](https://pepy.tech/project/django-modern-rpc)
[![Tests](https://github.com/alorence/django-modern-rpc/actions/workflows/default.yml/badge.svg)](https://github.com/alorence/django-modern-rpc/actions/workflows/default.yml)
[![Documentation Status](https://readthedocs.org/projects/django-modern-rpc/badge/?version=latest)](https://django-modern-rpc.readthedocs.io/en/latest/?badge=main)
[![Link to demo](https://img.shields.io/badge/demo-online-informational.svg)](https://modernrpc.onrender.com)

Expose global python functions through XML-RPC and/or JSON-RPC server using Django toolbox.

## Main features

- XML-RPC and JSON-RPC 2.0 support (JSON-RPC 1.0 is NOT supported)
- HTTP Basic Auth & custom authentication methods
- Multiple entry-points: group your RPC methods under different paths to apply
specific rules, authentication, protocol support, etc.
- API docs generation (based on docstring)

## Requirements

The following Django / Python version are supported, according to Django requirements (see
[here](https://docs.djangoproject.com/fr/2.2/faq/install/#faq-python-version-support) and
[here](https://docs.djangoproject.com/fr/4.2/faq/install/#faq-python-version-support))

| 🠗 Django \ Python 🠖 | 3.5  | 3.6 | 3.7 | 3.8 | 3.9 | 3.10 | 3.11| 3.12 |
|---------------------|-----|-----|-----|-----|-----|-------|-----|------|
| 2.1                 |  ✔️️ | ✔️️  | ✔️️  | ❌  | ❌  |  ❌  |  ❌  |  ❌ |
| 2.2                 |  ✔️️ | ✔️️  | ✔️️  | ✔️️  | ✔️️  |  ❌  |  ❌  |  ❌ |
| 3.0                 |  ❌ | ✔️️  | ✔️️  | ✔️️  | ✔️️  |  ❌  |  ❌  |  ❌ |
| 3.1                 |  ❌ | ✔️️  | ✔️️  | ✔️️  | ✔️️  |  ❌  |  ❌  |  ❌ |
| 3.2                 |  ❌ | ✔️️  | ✔️️  | ✔️️  | ✔️️  |  ✔️️  |  ❌  |  ❌ |
| 4.0                 |  ❌ | ❌  | ❌  | ✔️️  | ✔️️  |  ✔️️  |  ❌  |  ❌ |
| 4.1                 |  ❌ | ❌  | ❌  | ✔️️  | ✔️️  |  ✔️️  |  ✔️️  |  ❌ |
| 4.2                 |  ❌ | ❌  | ❌  | ✔️️  | ✔️️  |  ✔️️  |  ✔️️  |  ✔️️ |

## Setup

A [quick start](https://django-modern-rpc.readthedocs.io/en/latest/basics/quickstart.html) is available as part
of the documentation to help setting up you project.

## Code quality

Continuous integration and code analysis is performed automatically to ensure a decent code quality. Project health
is publicly available on following apps:

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/37607e2ecaf549b890fc6defca88c7f8)](https://www.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alorence/django-modern-rpc&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/37607e2ecaf549b890fc6defca88c7f8)](https://www.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alorence/django-modern-rpc&utm_campaign=Badge_Coverage)
[![Coveralls Status](https://coveralls.io/repos/github/alorence/django-modern-rpc/badge.svg)](https://coveralls.io/github/alorence/django-modern-rpc)
