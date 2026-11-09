#!/bin/bash

cd "$(dirname "$0")/backend"

PYTHONPATH=.:.. python -m uvicorn app.main:app --reload
