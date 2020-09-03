#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
cd ../..

export TITLE="ResNet on ImageNet"
export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/resnet-imagenet-"
export OUTPUT_FILE="output/resnet_accuracy.pdf"
./plot_accuracy.py "$DATA_FILE_PREFIX"*txt

