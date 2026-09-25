#!/bin/bash
# Runs Copilot's Python translation (unedited) on the same test data.
set -e
H=$(cd "$(dirname "$0")" && pwd); W=$H/run-python; rm -rf $W; mkdir -p $W; cd $W
for f in cardxref acctdata discgrp; do cp $H/data/$f.txt $f.txt; done
cp $H/data/${1:-tcatbal-TEST}.txt tcatbal.txt
python3 $H/python/${2:-cbact04c_copilot}.py 2022071800 > python-sysout.txt 2>&1 || echo "RUN ENDED WITH RC=$?"
echo "--- Python run finished: $(grep -c '' systran.txt) transactions written"
