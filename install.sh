#!/usr/bin/env bash

make initdb
make migrate
make upgrade
