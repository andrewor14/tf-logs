#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
cd ../..

export TITLE="ResNet on ImageNet"
export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/resnet-imagenet-"
export OUTPUT_FILE="output/resnet-imagenet-V100.pdf"
export SMOOTH_FACTOR="2"
export FIGURE_SIZE="6.7,5.7"
export YLIM="0.1,0.8"
export PLOT_BASELINE_FIRST="true"
./plot_accuracy.py $(ls ${DATA_FILE_PREFIX}*txt | grep -v time | xargs)

export OUTPUT_FILE="output/resnet-imagenet-V100-time.pdf"
export DATA_FILE_SUFFIX="-time.txt"
export XLABEL="Time elapsed (s)"
./plot_accuracy.py "$DATA_FILE_PREFIX"*-time.txt

export OUTPUT_FILE="output/resnet-imagenet-V100-time-2.pdf"
export FIGURE_SIZE="8,4"
export NUM_TOTAL_EXAMPLES="$((1281167 * 90))"
export GROUP_BARS="true"
export SPACE_YTICKS_APART="true"
./plot_time.py "$DATA_FILE_PREFIX"*-time.txt

