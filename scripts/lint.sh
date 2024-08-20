#!/usr/bin/env bash

set -e
set -x

ruff check duck_chat tests
ruff format duck_chat tests --check
mypy duck_chat
