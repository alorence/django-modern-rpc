# django-modern-rpc

[![Tests](https://img.shields.io/github/actions/workflow/status/alorence/django-modern-rpc/default.yml?style=for-the-badge&logo=github)](https://github.com/alorence/django-modern-rpc/actions/workflows/default.yml)
[![Documentation Status](https://img.shields.io/readthedocs/django-modern-rpc?style=for-the-badge&logo=readthedocs)](https://django-modern-rpc.readthedocs.io/en/latest/?badge=main)
[![Downloads](https://img.shields.io/pepy/dt/django-modern-rpc?style=for-the-badge&logo=python)](https://pepy.tech/project/django-modern-rpc)
[![Link to demo](https://img.shields.io/badge/Demo-Online-923456?style=for-the-badge&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBVcGxvYWRlZCB0bzogU1ZHIFJlcG8sIHd3dy5zdmdyZXBvLmNvbSwgR2VuZXJhdG9yOiBTVkcgUmVwbyBNaXhlciBUb29scyAtLT4NCjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+DQo8c3ZnIGZpbGw9IiMwMDAwMDAiIHZlcnNpb249IjEuMSIgaWQ9IkNhcGFfMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczp4bGluaz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94bGluayIgDQoJIHdpZHRoPSI4MDBweCIgaGVpZ2h0PSI4MDBweCIgdmlld0JveD0iMCAwIDQ0Mi4yNDYgNDQyLjI0NiINCgkgeG1sOnNwYWNlPSJwcmVzZXJ2ZSI+DQo8Zz4NCgk8Zz4NCgkJPHBhdGggZD0iTTQwOS42NTcsMzIuNDc0Yy00My4xNDYtNDMuMTQ2LTExMy44MzItNDMuMTQ2LTE1Ni45NzgsMGwtODQuNzYzLDg0Ljc2MmMyOS4wNy04LjI2Miw2MC41ODktNi4xMiw4OC4xMjksNi43MzINCgkJCWw0NC4wNjMtNDQuMDY0YzE3LjEzNi0xNy4xMzYsNDQuOTgyLTE3LjEzNiw2Mi4xMTgsMGMxNy4xMzYsMTcuMTM2LDE3LjEzNiw0NC45ODIsMCw2Mi4xMThsLTU1LjM4Niw1NS4zODZsLTM2LjQxNCwzNi40MTQNCgkJCWMtMTcuMTM2LDE3LjEzNi00NC45ODIsMTcuMTM2LTYyLjExOSwwbC00Ny40Myw0Ny40M2MxMS4wMTYsMTEuMDE3LDIzLjg2OCwxOS4yNzgsMzcuMzMyLDI0LjQ4DQoJCQljMzYuNDE1LDE0LjM4Miw3OC42NDMsOC44NzQsMTEwLjQ2Ny0xNi4yMTljMy4wNi0yLjQ0Nyw2LjQyNi01LjIwMSw5LjE4LTguMjYybDU3LjIyMi01Ny4yMjJsMzQuNTc4LTM0LjU3OA0KCQkJQzQ1My4xMDksMTQ2LjMwNiw0NTMuMTA5LDc1LjkyNiw0MDkuNjU3LDMyLjQ3NHoiLz4NCgkJPHBhdGggZD0iTTE4NC4xMzUsMzIwLjExNGwtNDIuMjI4LDQyLjIyOGMtMTcuMTM2LDE3LjEzNy00NC45ODIsMTcuMTM3LTYyLjExOCwwYy0xNy4xMzYtMTcuMTM2LTE3LjEzNi00NC45ODEsMC02Mi4xMTgNCgkJCWw5MS44LTkxLjc5OWMxNy4xMzYtMTcuMTM2LDQ0Ljk4Mi0xNy4xMzYsNjIuMTE5LDBsNDcuNDMtNDcuNDNjLTExLjAxNi0xMS4wMTYtMjMuODY4LTE5LjI3OC0zNy4zMzItMjQuNDgNCgkJCWMtMzguMjUtMTUuMy04My4yMzItOC4yNjItMTE1LjM2MiwyMC41MDJjLTEuNTMsMS4yMjQtMy4wNiwyLjc1NC00LjI4NCwzLjk3OGwtOTEuOCw5MS43OTkNCgkJCWMtNDMuMTQ2LDQzLjE0Ni00My4xNDYsMTEzLjgzMiwwLDE1Ni45NzljNDMuMTQ2LDQzLjE0NiwxMTMuODMyLDQzLjE0NiwxNTYuOTc4LDBsODIuOTI3LTgzLjg0NQ0KCQkJQzIzMC4wMzUsMzM1LjcxOSwyMjAuMjQzLDMzNC40OTYsMTg0LjEzNSwzMjAuMTE0eiIvPg0KCTwvZz4NCjwvZz4NCjwvc3ZnPg==)](https://modernrpc.onrender.com)

Expose global python functions through XML-RPC and/or JSON-RPC server using Django toolbox.

## Main features

- XML-RPC and JSON-RPC 2.0 support (JSON-RPC 1.0 is NOT supported)
- HTTP Basic Auth & custom authentication methods
- Multiple entry-points: group your RPC methods under different paths to apply
  specific rules, authentication, protocol support, etc.
- API docs generation (based on docstring)

## Requirements

The following Django / Python versions are supported, according to [Django Installation FAQ](https://docs.djangoproject.com/en/5.1/faq/install/#what-python-version-can-i-use-with-django)

|   Python ➞ | 3.8 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 |
|-----------:|:---:|:---:|:----:|:----:|:----:|:----:|
| Django 3.2 | 🟢  | 🟢  |  🟢  |  🔴  |  🔴  |  🔴  |
| Django 4.0 | 🟢  | 🟢  |  🟢  |  🔴  |  🔴  |  🔴  |
| Django 4.1 | 🟢  | 🟢  |  🟢  |  🟢  |  🔴  |  🔴  |
| Django 4.2 | 🟢  | 🟢  |  🟢  |  🟢  |  🟢  |  🔴  |
| Django 5.0 | 🔴  | 🔴  |  🟢  |  🟢  |  🟢  |  🔴  |
| Django 5.1 | 🔴  | 🔴  |  🟢  |  🟢  |  🟢  |  🟢  |
| Django 5.2 | 🔴  | 🔴  |  🟢  |  🟢  |  🟢  |  🟢  |

## Setup

A [quick start](https://django-modern-rpc.readthedocs.io/en/latest/basics/quickstart.html) is available as part
of the documentation to help setting up you project.

## Code quality

Continuous integration and code analysis is performed automatically to ensure a decent code quality. Project health
is publicly available on following apps:

[![Coveralls](https://img.shields.io/coverallsCoverage/github/alorence/django-modern-rpc?style=for-the-badge&logo=coveralls)](https://coveralls.io/github/alorence/django-modern-rpc)
[![Codacy Coverage](https://img.shields.io/codacy/coverage/37607e2ecaf549b890fc6defca88c7f8?style=for-the-badge&logo=codacy)](https://app.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)
[![Codacy Grade](https://img.shields.io/codacy/grade/37607e2ecaf549b890fc6defca88c7f8?style=for-the-badge&logo=codacy)](https://app.codacy.com/gh/alorence/django-modern-rpc/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
