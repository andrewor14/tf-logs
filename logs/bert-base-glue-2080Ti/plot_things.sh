#!/bin/bash

CURRENT_DIR="$(basename $PWD)"
GLUE_TASKS="SST-2 QNLI CoLA"
cd ../..

for glue_task in $GLUE_TASKS; do
  export TITLE="BERT (base) GLUE $glue_task on 1 GPU"
  export DATA_FILE_PREFIX="logs/${CURRENT_DIR}/bert-glue-${glue_task}-"
  OUTPUT_FILE_PREFIX="bert-glue-${glue_task}-2080Ti"
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}.pdf" STEPS_PER_EPOCH="100"\
    ./plot_accuracy.py "$DATA_FILE_PREFIX"*bs.txt
  OUTPUT_FILE="${OUTPUT_FILE_PREFIX}-time.pdf" XLABEL="Time elapsed (s)"\
    DATA_FILE_SUFFIX="-time.txt" ./plot_accuracy.py "$DATA_FILE_PREFIX"*time.txt
done

