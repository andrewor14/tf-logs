#!/bin/bash

export COMM="${COMM:=0.7664}"

cd ../models/virtual

ANSWER=""
function solve() {
  export FIXED_BATCH_SIZES=$1
  NUM_V100=$2
  NUM_P100=$3
  ANSWER="$ANSWER, $(./brute_het.py 8192 $NUM_V100 profile/resnet-imagenet-V100.txt\
    $NUM_P100 profile/resnet-imagenet-P100.txt | grep Throughput | tail -n 1 | awk '{print $2}')"
}

solve 256,256 2 2
solve 192,256 2 2
solve 96,256 2 2
solve 192,256 2 4
solve 192,128 2 4
solve 192,64 2 4
solve 192,32 2 4
solve 256,256 2 8

echo "${ANSWER/, /}"

cd - > /dev/null

