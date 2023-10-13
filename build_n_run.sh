#!/bin/bash
poetry build
docker build -t rc_demo .
docker compose up --remove-orphans