#!/usr/bin/env bash

set -e
set -x

mypy duck_chat
ruff check duck_chat tests
ruff format duck_chat tests --check
