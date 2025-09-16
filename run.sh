#!/usr/bin/env bash
docker run -d \
  --name dev_container \
  -p 8080:8000 \
  -v "$(pwd):/workspace" \
  ultralytics/ultralytics:latest-cpu

