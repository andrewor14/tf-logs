#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
cd ../..

export TITLE="ResNet on ImageNet"
export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/resnet-imagenet-"
export OUTPUT_FILE="output/resnet-imagenet-V100.pdf"
export SMOOTH_FACTOR="2"
export FIGURE_SIZE="6.5,5.5"
./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*txt | grep -v time | xargs)

export OUTPUT_FILE="output/resnet-imagenet-V100-time.pdf"
export DATA_FILE_SUFFIX="-time.txt"
export XLABEL="Time elapsed (s)"
./plot_accuracy.py "$DATA_FILE_PREFIX"*-time.txt

export OUTPUT_FILE="output/resnet-imagenet-V100-time-2.pdf"
export FIGURE_SIZE="13,6"
export TIME_UNIT="h"
./plot_time.py "$DATA_FILE_PREFIX"*-time.txt

