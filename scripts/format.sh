#!/usr/bin/env bash
set -x

ruff check duck_chat tests --fix
ruff format duck_chat tests

