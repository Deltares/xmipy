#!/bin/bash
set -e

if [ "${RUN_TYPE}" = "test" ]; then
  echo "Running amipy autotest suite..."
  nosetests -v --with-id --with-timer -w ./autotest \
     --with-coverage --cover-package=amipy
elif [ "${RUN_TYPE}" = "style" ]; then
  echo "Checking Python code with flake8..."
  if ! flake8; then
    echo "An error occurred while running flake8." >&2
    exit 1
  fi
else
  echo "Unhandled RUN_TYPE=${RUN_TYPE}" >&2
  exit 1
fi
