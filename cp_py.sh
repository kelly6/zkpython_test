#!/bin/bash

mkdir -p server/ser1
mkdir -p server/ser2
mkdir -p server/ser3

mkdir -p client/cli1
mkdir -p client/cli2
mkdir -p client/cli3
mkdir -p client/cli4
mkdir -p client/cli5
mkdir -p client/cli6

cp server/ser1/config.py server/ser1/config.py.backup
cp server/ser2/config.py server/ser2/config.py.backup
cp server/ser3/config.py server/ser3/config.py.backup

cp client/cli1/config.py client/cli1/config.py.backup
cp client/cli2/config.py client/cli2/config.py.backup
cp client/cli3/config.py client/cli3/config.py.backup
cp client/cli4/config.py client/cli4/config.py.backup
cp client/cli5/config.py client/cli5/config.py.backup
cp client/cli6/config.py client/cli6/config.py.backup

cp *.py server/ser1/
cp *.py server/ser2/
cp *.py server/ser3/

cp *.py client/cli1/
cp *.py client/cli2/
cp *.py client/cli3/
cp *.py client/cli4/
cp *.py client/cli5/
cp *.py client/cli6/

cp server/ser1/config.py.backup server/ser1/config.py
cp server/ser2/config.py.backup server/ser2/config.py
cp server/ser3/config.py.backup server/ser3/config.py
                               
cp client/cli1/config.py.backup client/cli1/config.py
cp client/cli2/config.py.backup client/cli2/config.py
cp client/cli3/config.py.backup client/cli3/config.py
cp client/cli4/config.py.backup client/cli4/config.py
cp client/cli5/config.py.backup client/cli5/config.py
cp client/cli6/config.py.backup client/cli6/config.py

