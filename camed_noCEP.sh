#!/bin/bash

# This variable is responsible to create a file with an specific RUN value.
export RUN=1

docker network create mqtt-net;timeout 130s python3 camed_noCEP.py;